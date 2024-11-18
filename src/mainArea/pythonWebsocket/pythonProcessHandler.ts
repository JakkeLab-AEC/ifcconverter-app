import { spawn, ChildProcessWithoutNullStreams } from 'node:child_process';

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

        this.pyProcess = spawn('python', [this.scriptPath]);

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