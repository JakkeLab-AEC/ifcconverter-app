import { PythonProcessHandler } from "./pythonWebsocket/pythonProcessHandler";
import { PythonWebsocket } from "./pythonWebsocket/pywsClient";
import path from 'path';

export class AppController {
    private static Instance: AppController;
    
    private pythonProcessHandler: PythonProcessHandler;

    getPythonProcessHandler() {
        return this.pythonProcessHandler;
    }

    private constructor() {
        const pythonScriptPath = path.resolve(__dirname, '../mainPython/main.py');
        this.pythonProcessHandler = new PythonProcessHandler(pythonScriptPath);
    }

    public static InitiateAppController(){
        AppController.Instance = new AppController();
    }

    public static getInstance(){
        return AppController.Instance;
    }
}