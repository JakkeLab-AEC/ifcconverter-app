import { getCurrentTimestamp } from '../../commonUtils/timeStamper';
import { AppController } from '../appController/appController';
import { spawn, ChildProcessWithoutNullStreams } from 'node:child_process';
import path from 'path';

export class PythonProcessHandler {
    private pyProcess: ChildProcessWithoutNullStreams | null = null;
    private scriptPath: string;

    constructor(scriptPath: string) {
        this.scriptPath = scriptPath;
    }

    start(): void {
        if (this.pyProcess) {
            console.warn('Python process is already running.');
            return;
        }
        
        // Python 실행 파일 경로
        let embeddedPythonPath = "";
        if(AppController.getInstance().osInfo == "win") {
            embeddedPythonPath = "python.exe";
        } else {
            embeddedPythonPath = "bin/python"
        }
        const pythonExecutable = path.resolve(__dirname, `../../conda_env/${embeddedPythonPath}`);
        console.log('Python Executable Path:', pythonExecutable);
        console.log('Python Script Path:', this.scriptPath);

        // Python 프로세스 실행
        try {
            this.pyProcess = spawn(pythonExecutable, [this.scriptPath], {
                stdio: ['pipe', 'pipe', 'pipe'], // stdin, stdout, stderr
            });
    
            this.pyProcess.stderr.on('data', (data) => {
                console.error(`Python stderr: ${data}`);
            });
    
            this.pyProcess.on('close', (code) => {
                console.log(`Python process exited with code ${code}`);
                this.pyProcess = null;
            });
        } catch(error) {
            console.error(error);
        }
    }

    stop(): void {
        if (this.pyProcess) {
            this.pyProcess.kill();
            console.log('Python process terminated.');
            this.pyProcess = null;
        } else {
            console.warn('Python process is not running.');
        }
    }

    async sendMessage(data: object, countListner?: (count: number, message: string) => void): Promise<any> {
        if(!this.pyProcess) {
            throw new Error('Python process is not running.');
        }
        
        let count = 0;
        return new Promise((resolve, reject) => {
            const message = JSON.stringify(data) + '\n';
            const [stdin, stdout] = [this.pyProcess?.stdin, this.pyProcess?.stdout];
            
            if(!stdin || !stdout) {
                return reject('Python process stdin or stdout is not available.');
            }

            stdout.removeAllListeners('data');

            let buffer = '';
            let jsonBuffer: string[] = [];
            const onData = (chunk: Buffer) => {
                buffer += chunk.toString();
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    jsonBuffer.push(line);
                }
                
                const joinedBuffer = jsonBuffer.join('');
                const parseJob = JSON.tryParse<Object>(joinedBuffer);
                let parsedData;
                if(parseJob.success && Object.keys(parseJob.data).includes("action") && Object.keys(parseJob.data).includes("result")) {
                    parsedData = parseJob.data;
                    count++;
                }

                jsonBuffer.length = 0;
                buffer = '';
                
                if(countListner && parseJob.success) {
                    let message: string = "";
                    const timestamp = getCurrentTimestamp();
                    const writingResult = parsedData.result ? "done" : "failed";
                    switch(parsedData.action) {
                        case "writingEntity":
                            message = `[${timestamp}] Writing ${parsedData.entityType} is ${writingResult}`;
                            break;
                        case "writingFile":
                            message = `[${timestamp}] Writing IFC file is ${writingResult}`;
                            break;
                        default:
                            return;
                    }
                    
                    countListner(count, message);
                }                
            };

            stdout.on('data', onData);
            
            stdin.write(message); // Python으로 요청 전송
        });
    }

    isRunning(): boolean {
        return this.pyProcess !== null;
    }
}

