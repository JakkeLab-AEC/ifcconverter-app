import { create } from "zustand";

interface homeStatusProps {
    osName: string;
    mode: 'dist'|'dev';
    setOSName: (name: string) => void;
    setMode: (mode: 'dist'|'dev') => void;
}

export const useHomeStore = create<homeStatusProps>((set, get) => ({
    osName: '',
    mode: 'dist',
    setOSName: (name: string) => {
        set(() => {
            return {osName: name}
        })
    },
    setMode: (mode: 'dist'|'dev') => {
        set(() => {
            return {mode : mode}
        })
    }
}));