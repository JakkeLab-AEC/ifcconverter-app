import { useHomeStore } from './rendererArea/homeStore';
import './app';

window.electronSystemAPI.receiveOSInfo((callback) => {
    useHomeStore.getState().setOSName(callback.platform);
    useHomeStore.getState().setMode(callback.mode);
});