let pc = null;
let isConnected = false;

function log(message) {
    const logs = document.getElementById('logs');
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry';
    logEntry.textContent = `${new Date().toLocaleTimeString()}: ${message}`;
    logs.appendChild(logEntry);
    logs.scrollTop = logs.scrollHeight;
}

function updateStatus(status) {
    document.getElementById('status').textContent = status;
}

function updateButton() {
    const btn = document.getElementById('connect-btn');
    if (isConnected) {
        btn.textContent = 'Desconectar';
        btn.style.background = '#f44336';
    } else {
        btn.textContent = 'Conectar';
        btn.style.background = '#4CAF50';
    }
}

async function createSmallWebRTCConnection() {
    const configuration = {
        iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
    };
    
    pc = new RTCPeerConnection(configuration);
    
    // Configurar manejo de audio remoto
    pc.ontrack = (event) => {
        log('Recibiendo stream de audio remoto');
        const audioEl = document.getElementById('audio-el');
        if (audioEl) {
            audioEl.srcObject = event.streams[0];
        }
    };
    
    // Configurar estados de conexión
    pc.onconnectionstatechange = () => {
        log(`Estado de conexión: ${pc.connectionState}`);
        if (pc.connectionState === 'connected') {
            updateStatus('🟢 Conectado - Escuchando...');
            isConnected = true;
            updateButton();
        } else if (pc.connectionState === 'disconnected' || pc.connectionState === 'failed') {
            updateStatus('🔴 Desconectado');
            isConnected = false;
            updateButton();
        }
    };
    
    pc.oniceconnectionstatechange = () => {
        log(`Estado ICE: ${pc.iceConnectionState}`);
    };
    
    // Obtener audio del micrófono
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true
            } 
        });
        
        log('Micrófono obtenido exitosamente');
        stream.getTracks().forEach(track => {
            pc.addTrack(track, stream);
        });
        
    } catch (error) {
        log(`Error al obtener micrófono: ${error.message}`);
        throw error;
    }
    
    // Crear oferta
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    
    log('Enviando oferta al servidor...');
    
    // Enviar oferta al backend
    try {
        const response = await fetch('http://localhost:8004/api/v1/offer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                sdp: offer.sdp,
                type: offer.type
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const answer = await response.json();
        log('Respuesta recibida del servidor');
        
        // Configurar descripción remota
        await pc.setRemoteDescription(new RTCSessionDescription({
            type: answer.type,
            sdp: answer.sdp
        }));
        
        log('Conexión WebRTC establecida exitosamente');
        
    } catch (error) {
        log(`Error al conectar con el servidor: ${error.message}`);
        throw error;
    }
}

async function connect() {
    if (isConnected) {
        // Desconectar
        if (pc) {
            pc.close();
            pc = null;
        }
        updateStatus('🔴 Desconectado');
        isConnected = false;
        updateButton();
        log('Conexión cerrada');
        return;
    }
    
    try {
        updateStatus('🟡 Conectando...');
        log('Iniciando conexión WebRTC...');
        
        await createSmallWebRTCConnection();
        
    } catch (error) {
        log(`Error de conexión: ${error.message}`);
        updateStatus('❌ Error de conexión');
        isConnected = false;
        updateButton();
    }
}

// Inicializar la aplicación
document.addEventListener('DOMContentLoaded', () => {
    const connectBtn = document.getElementById('connect-btn');
    connectBtn.addEventListener('click', connect);
    
    updateStatus('🔴 Desconectado');
    updateButton();
    
    log('Aplicación inicializada');
    log('Haz clic en "Conectar" para iniciar la conversación');
});