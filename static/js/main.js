// Arogya Doctor Vision - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const instructionsPanel = document.querySelector('.instructions-panel');
    const instructionsContent = document.querySelector('.instructions-content');
    const startRecordingBtn = document.getElementById('start-recording');
    const stopRecordingBtn = document.getElementById('stop-recording');
    const playAudioBtn = document.getElementById('play-audio');
    const recordedAudio = document.getElementById('recorded-audio');
    const audioVisualizer = document.querySelector('.audio-visualizer');
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    const fileSelectBtn = document.getElementById('file-select-btn');
    const imagePreview = document.getElementById('image-preview');
    const previewImg = document.getElementById('preview-img');
    const clearBtn = document.getElementById('clear-btn');
    const diagnoseBtn = document.getElementById('diagnose-btn');
    const transcriptionOutput = document.getElementById('transcription-output');
    const diagnosisOutput = document.getElementById('diagnosis-output');
    const diagnosisAudio = document.getElementById('diagnosis-audio');
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingStatus = document.getElementById('loading-status');
    const progressFill = document.querySelector('.progress-fill');

    // Variables
    let mediaRecorder;
    let audioChunks = [];
    let audioBlob = null;
    let imageFile = null;

    // API Status check removed as requested

    // Tab Switching
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons and panes
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));

            // Add active class to clicked button and corresponding pane
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });

    // Instructions Panel Toggle
    instructionsPanel.querySelector('h3').addEventListener('click', () => {
        instructionsContent.style.display = instructionsContent.style.display === 'none' ? 'block' : 'none';
    });

    // Audio Recording
    startRecordingBtn.addEventListener('click', startRecording);
    stopRecordingBtn.addEventListener('click', stopRecording);
    playAudioBtn.addEventListener('click', playRecording);

    function startRecording() {
        audioChunks = [];

        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);

                mediaRecorder.addEventListener('dataavailable', event => {
                    audioChunks.push(event.data);
                });

                mediaRecorder.addEventListener('stop', () => {
                    audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const audioUrl = URL.createObjectURL(audioBlob);
                    recordedAudio.src = audioUrl;

                    // Enable play button
                    playAudioBtn.disabled = false;

                    // Check if both audio and image are ready
                    checkReadyState();
                });

                // Start recording
                mediaRecorder.start();

                // Update UI
                startRecordingBtn.disabled = true;
                stopRecordingBtn.disabled = false;
                audioVisualizer.classList.add('active');

                // Animate record button
                document.querySelector('.record-button').classList.add('recording');
            })
            .catch(error => {
                console.error('Error accessing microphone:', error);
                alert('Error accessing microphone. Please make sure your microphone is connected and you have granted permission to use it.');
            });
    }

    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();

            // Stop all tracks in the stream
            mediaRecorder.stream.getTracks().forEach(track => track.stop());

            // Update UI
            startRecordingBtn.disabled = false;
            stopRecordingBtn.disabled = true;
            audioVisualizer.classList.remove('active');

            // Stop animating record button
            document.querySelector('.record-button').classList.remove('recording');
        }
    }

    function playRecording() {
        recordedAudio.play();
    }

    // Image Upload
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });

    dropArea.addEventListener('drop', handleDrop, false);
    fileSelectBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight() {
        dropArea.classList.add('highlight');
    }

    function unhighlight() {
        dropArea.classList.remove('highlight');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0 && files[0].type.startsWith('image/')) {
            handleFiles(files);
        } else {
            alert('Please drop an image file.');
        }
    }

    function handleFileSelect(e) {
        const files = e.target.files;

        if (files.length > 0) {
            handleFiles(files);
        }
    }

    function handleFiles(files) {
        imageFile = files[0];

        // Show preview
        const reader = new FileReader();
        reader.onload = function(e) {
            previewImg.src = e.target.result;
            imagePreview.style.display = 'block';
            dropArea.style.display = 'none';
        };
        reader.readAsDataURL(imageFile);

        // Check if both audio and image are ready
        checkReadyState();
    }

    // Clear Button
    clearBtn.addEventListener('click', () => {
        // Clear audio
        audioBlob = null;
        recordedAudio.src = '';
        playAudioBtn.disabled = true;

        // Clear image
        imageFile = null;
        previewImg.src = '';
        imagePreview.style.display = 'none';
        dropArea.style.display = 'block';

        // Clear outputs
        transcriptionOutput.textContent = '';
        diagnosisOutput.textContent = '';
        diagnosisAudio.src = '';

        // Update button state
        diagnoseBtn.disabled = true;
    });

    // Check if ready for diagnosis
    function checkReadyState() {
        diagnoseBtn.disabled = !(audioBlob && imageFile);
    }

    // Diagnose Button
    diagnoseBtn.addEventListener('click', () => {
        if (!audioBlob || !imageFile) {
            alert('Please record audio and upload an image before getting a diagnosis.');
            return;
        }

        // Show loading overlay
        loadingOverlay.classList.add('active');

        // Create form data
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.wav');
        formData.append('image', imageFile);

        // Animate progress
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 5;
            if (progress > 90) {
                clearInterval(progressInterval);
            }
            progressFill.style.width = `${progress}%`;
        }, 500);

        // Update loading status messages
        const statusMessages = [
            'Recording transcription in progress...',
            'Analyzing image...',
            'Dr. Arogya is thinking...',
            'Generating diagnosis...',
            'Preparing audio response...'
        ];

        let messageIndex = 0;
        const messageInterval = setInterval(() => {
            loadingStatus.textContent = statusMessages[messageIndex];
            messageIndex = (messageIndex + 1) % statusMessages.length;
        }, 3000);

        // Send request
        fetch('/api/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Clear intervals
            clearInterval(progressInterval);
            clearInterval(messageInterval);

            if (data.status === 'success') {
                // Complete progress bar
                progressFill.style.width = '100%';

                // Update outputs
                transcriptionOutput.textContent = data.transcription;
                diagnosisOutput.textContent = data.diagnosis;
                diagnosisAudio.src = data.audio_response;

                // Hide loading overlay after a short delay
                setTimeout(() => {
                    loadingOverlay.classList.remove('active');
                }, 1000);

                // Scroll to results
                document.querySelector('.output-section').scrollIntoView({ behavior: 'smooth' });
            } else {
                // Hide loading overlay
                loadingOverlay.classList.remove('active');

                // Show error
                alert(`Error: ${data.message}`);
            }
        })
        .catch(error => {
            // Clear intervals
            clearInterval(progressInterval);
            clearInterval(messageInterval);

            // Hide loading overlay
            loadingOverlay.classList.remove('active');

            // Show error
            alert(`Error: ${error.message}`);
        });
    });

    // Add animations to elements when they come into view
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.input-card, .output-card');

        elements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementBottom = element.getBoundingClientRect().bottom;

            if (elementTop < window.innerHeight && elementBottom > 0) {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        });
    };

    // Initial animation
    setTimeout(animateOnScroll, 500);

    // Listen for scroll events
    window.addEventListener('scroll', animateOnScroll);
});
