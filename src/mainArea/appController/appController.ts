import { PythonProcessHandler } from "../processHandler/pythonProcessHandler";
import { DataStoreService } from "./services/dataStoreService";
import path from 'path';

export class AppController {
    private static Instance: AppController;
    
    private pythonProcessHandler: PythonProcessHandler;
    private dataStoreService: DataStoreService;
    readonly osInfo: "win"|"mac";

    getPythonProcessHandler() {
        return this.pythonProcessHandler;
    }

    getDataStore() {
        return this.dataStoreService;
    }

    private constructor(osInfo: "win"|"mac" = "mac") {
        const pythonScriptPath = path.resolve(__dirname, '../../mainPython/main.py');
        this.pythonProcessHandler = new PythonProcessHandler(pythonScriptPath);
        this.dataStoreService = new DataStoreService();
        this.osInfo = osInfo;
    }

    public static InitiateAppController(osInfo: "win"|"mac" = "mac"){
        AppController.Instance = new AppController(osInfo);
    }

    public static getInstance(){
        return AppController.Instance;
    }
}