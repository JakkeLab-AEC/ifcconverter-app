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
        const pythonExecutable = path.resolve(__dirname, '../../anaconda_env/python.exe');
        console.log('Python Executable Path:', pythonExecutable);
        console.log('Python Script Path:', this.scriptPath);

        // Python 프로세스 실행
        try {
            this.pyProcess = spawn(pythonExecutable, [this.scriptPath], {
                stdio: ['pipe', 'pipe', 'pipe'], // stdin, stdout, stderr
            });

            this.pyProcess.stdout.on('data', (data) => {
                console.log(`Python stdout: ${data}`);
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

    async sendMessage(data: object): Promise<any> {
        if(!this.pyProcess) {
            throw new Error('Python process is not running.');
        }

        return new Promise((resolve, reject) => {
            const message = JSON.stringify(data) + '\n';
            const [stdin, stdout] = [this.pyProcess?.stdin, this.pyProcess?.stdout];

            if(!stdin || !stdout) {
                return reject('Python process stdin or stdout is not available.');
            }

            let buffer = '';

            const onData = (chunk: Buffer) => {
                console.log(`------Chunk Received------`);
                console.log(chunk.toString());
                console.log(`--------------------------`);
    
                buffer += chunk.toString(); // 버퍼를 문자열로 추가
                if (buffer.trim().endsWith('}')) { // JSON 끝 확인
                    try {
                        const parsed = JSON.parse(buffer.trim()); // JSON 파싱
                        stdout.removeListener('data', onData); // 리스너 해제
                        resolve(parsed);
                    } catch (error) {
                        reject(`Failed to parse Python response: ${error}`);
                    }
                }
            };

            stdout.on('data', onData);
            
            stdin.write(message); // Python으로 요청 전송

            //  // 타임아웃 설정
            // setTimeout(() => {
            //     stdout.removeListener('data', onData);
            //     reject('Python process did not respond in time.');
            // }, 5000); // 5초 제한
        });
    }

    isRunning(): boolean {
        return this.pyProcess !== null;
    }
}