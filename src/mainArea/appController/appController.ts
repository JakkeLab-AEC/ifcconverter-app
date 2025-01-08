import { DataStoreService } from "./services/dataStoreService";

export class AppController {
    private static Instance: AppController;
    
    private dataStoreService: DataStoreService;
    readonly osInfo: "win"|"mac";

    getDataStore() {
        return this.dataStoreService;
    }

    private constructor(osInfo: "win"|"mac" = "mac") {
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