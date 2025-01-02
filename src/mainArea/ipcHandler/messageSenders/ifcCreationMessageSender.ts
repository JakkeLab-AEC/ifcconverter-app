import { UIController } from "../../appController/controllers/uicontroller";

interface IfcCreationMessageProps {
    totalSteps: number,
    currentStep: number,
    message: string
}

export function IfcCreationMessageSender(args: IfcCreationMessageProps) {
    const mainWindow = UIController.instance.getWindow('main-window');
    mainWindow?.webContents.send('send-ifc-creation-status', args);
}