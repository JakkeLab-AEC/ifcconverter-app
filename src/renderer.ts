import { useHomeStore } from './rendererArea/homeStore';
import { useConverterPageStore } from './rendererArea/pages/converter/converterPageStore';
import './app';

window.electronSystemAPI.receiveOSInfo((callback) => {
    useHomeStore.getState().setOSName(callback.platform);
    useHomeStore.getState().setMode(callback.mode);
});

window.electronIfcCreationAPI.receiveConvertProgress((callback) => {
    console.log(callback.currentStep*100/callback.totalSteps);
    useConverterPageStore.getState().setCurrentProgress(callback.currentStep*100/callback.totalSteps)
});