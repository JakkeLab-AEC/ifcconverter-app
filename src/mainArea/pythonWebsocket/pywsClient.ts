import WebSocket from 'ws';

export class PythonWebsocket {
    private ws: WebSocket;

    constructor(private url: string = 'ws://localhost:5666') {
        this.ws = new WebSocket(url);

        this.ws.onopen = this.onOpen.bind(this);
        this.ws.onmessage = this.onMessage.bind(this);
        this.ws.onerror = this.onError.bind(this);
        this.ws.onclose = this.onClose.bind(this);
    }

    private onOpen(): void {
        console.log('WebSocket connected');
        this.ws.send('Hello from Electron');
    }

    private onMessage(event: MessageEvent): void {
        console.log('Message from Python:', event.data);
    }

    private onError(event: Event): void {
        console.error('WebSocket error:', event);
    }

    private onClose(): void {
        console.log('WebSocket connection closed');
    }

    public sendMessage(message: string): void {
        if (this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(message);
        } else {
            console.warn('WebSocket is not open. Message not sent.');
        }
    }
}