let audioCtx = null;
let masterVolume = 0.7;

function initAudio() {
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
}

function playTone(freq, duration) {
    if (!audioCtx) return;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.frequency.value = freq;
    osc.type = 'sine';
    const now = audioCtx.currentTime;
    gain.gain.setValueAtTime(0, now);
    gain.gain.linearRampToValueAtTime(masterVolume, now + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);
    osc.start();
    osc.stop(now + duration);
}

function playWebSound(soundType) {
    fetch(`/api/sounds/${soundType}`)
        .then(res => res.json())
        .then(data => {
            const freqs = data.data.frequencies;
            const dur = data.data.duration;
            freqs.forEach((f, i) => {
                setTimeout(() => playTone(f, dur), i * 150);
            });
        })
        .catch(() => {
            const fallback = {
                win: [523.25, 659.25, 783.99],
                lose: [392, 349.23, 293.66, 261.63],
                achievement: [784, 987.77, 1174.66]
            };
            const freqs = fallback[soundType] || fallback.win;
            freqs.forEach((f, i) => setTimeout(() => playTone(f, 0.25), i * 120));
        });
}

window.GameSounds = { 
    playSound: function(type) { 
        console.log("Sound:", type); 
    } 
};