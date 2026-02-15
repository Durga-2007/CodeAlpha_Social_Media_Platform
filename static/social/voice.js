document.addEventListener('DOMContentLoaded', () => {
    const voiceBtn = document.getElementById('voice-btn');
    const statusText = document.getElementById('voice-status');
    const textArea = document.querySelector('.post-form textarea');

    if (!voiceBtn || !textArea) return;

    // Check for browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        voiceBtn.style.display = 'none';
        console.error('Speech recognition not supported in this browser.');
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    let isRecording = false;

    voiceBtn.addEventListener('click', () => {
        if (isRecording) {
            recognition.stop();
        } else {
            try {
                recognition.start();
            } catch (err) {
                console.error('Recognition start error:', err);
            }
        }
    });

    recognition.onstart = () => {
        isRecording = true;
        voiceBtn.classList.add('active');
        statusText.textContent = 'Listening...';
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        if (event.error === 'no-speech') {
            statusText.textContent = 'No speech detected.';
        } else {
            statusText.textContent = 'Error: ' + event.error;
        }
        stopRecording();
    };

    recognition.onend = () => {
        stopRecording();
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;

        if (textArea.value.trim().length > 0) {
            textArea.value += ' ' + transcript;
        } else {
            textArea.value = transcript;
        }

        statusText.textContent = 'Speech captured!';
        setTimeout(() => {
            if (!isRecording) statusText.textContent = '';
        }, 3000);
    };

    function stopRecording() {
        isRecording = false;
        voiceBtn.classList.remove('active');
        if (statusText.textContent === 'Listening...') {
            statusText.textContent = '';
        }
    }
});
