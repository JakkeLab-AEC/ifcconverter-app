import { PythonProcessHandler } from "./pythonWebsocket/pythonProcessHandler";
import { PythonWebsocket } from "./pythonWebsocket/pywsClient";
import path from 'path';

export class AppController {
    private static Instance: AppController;
    
    private pythonProcessHandler: PythonProcessHandler;
    // private pythonWebsocket: PythonWebsocket;

    getPythonProcessHandler() {
        return this.pythonProcessHandler;
    }

    getPythonWebSocket() {
        // return this.pythonWebsocket;
    }

    private constructor() {
        const pythonScriptPath = path.resolve(__dirname, '../mainPython/main.py');
        this.pythonProcessHandler = new PythonProcessHandler(pythonScriptPath);
        this.pythonProcessHandler.start();

        // this.pythonWebsocket = new PythonWebsocket('ws://localhost:5666');
    }

    public static InitiateAppController(){
        AppController.Instance = new AppController();
    }

    public static getInstance(){
        return AppController.Instance;
    }
}