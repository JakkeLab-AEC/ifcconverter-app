import { PythonProcessHandler } from "../processHandler/pythonProcessHandler";
import path from 'path';
import { DataStoreService } from "./services/dataStoreService";

export class AppController {
    private static Instance: AppController;
    
    private pythonProcessHandler: PythonProcessHandler;
    private dataStoreService: DataStoreService;

    getPythonProcessHandler() {
        return this.pythonProcessHandler;
    }

    getDataStore() {
        return this.dataStoreService;
    }

    private constructor() {
        const pythonScriptPath = path.resolve(__dirname, '../../mainPython/main.py');
        this.pythonProcessHandler = new PythonProcessHandler(pythonScriptPath);
        this.dataStoreService = new DataStoreService();
    }

    public static InitiateAppController(){
        AppController.Instance = new AppController();
    }

    public static getInstance(){
        return AppController.Instance;
    }
}