import { spawn, ChildProcessWithoutNullStreams } from 'node:child_process';
import path from 'path';

export class PythonProcessHandler {
    private pyProcess: ChildProcessWithoutNullStreams | null = null;
    private scriptPath: string;

    constructor(scriptPath: string) {
        this.scriptPath = scriptPath;
    }

    public start(): void {
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
                stdio: 'pipe', // 출력과 에러를 가져오기 위해 pipe 설정
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

    public stop(): void {
        if (this.pyProcess) {
            this.pyProcess.kill();
            console.log('Python process terminated.');
            this.pyProcess = null;
        } else {
            console.warn('Python process is not running.');
        }
    }

    public isRunning(): boolean {
        return this.pyProcess !== null;
    }
}