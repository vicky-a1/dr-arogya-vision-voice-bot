# Arogya Doctor Vision - Application Masterplan

## Project Overview

Arogya Doctor Vision is an AI-powered medical diagnosis assistant that helps users get preliminary insights about their medical conditions through image analysis and natural language processing. The application allows users to upload medical images, ask questions via voice recording, and receive professional medical assessments from an AI doctor (Dr. Arogya).

## Technical Specifications

### Frontend

#### Framework & Libraries
- **Framework**: Custom HTML/CSS/JavaScript (Vanilla JS)
- **CSS Preprocessor**: None (Pure CSS)
- **Icons**: Font Awesome 6.4.0
- **Fonts**: Poppins (300, 400, 500, 600, 700 weights)

#### Color Palette
follow the color palette of this existing website

#### Layout & Components

1. **Header**
   - Logo animation (pulsing circle)
   - Application title: "Arogya Doctor Vision"
   - Subtitle: "AI-Powered Medical Diagnosis Assistant"

2. **Tab Navigation**
   - Diagnosis Tab (default active)
   - About Tab

3. **Diagnosis Tab Content**
   - Instructions panel (collapsible)
   - Two-column layout for input and output sections on desktop
   - Single-column layout on mobile (stacked)

4. **Input Section**
   - Voice Recording Component
     - Microphone button with animation
     - Audio visualizer with animated bars
     - Control buttons (Start, Stop, Play)
   - Image Upload Component
     - Drag & drop area
     - File selection button
     - Image preview with responsive sizing
   - Action Buttons
     - Clear button (secondary style)
     - Get Diagnosis button (primary style)

5. **Output Section**
   - Transcribed Question Card
   - Dr. Arogya's Diagnosis Card (scrollable for long content)
   - Audio Response Player

6. **About Tab Content**
   - Project description
   - Features list
   - Important disclaimer in warning box
   - Contact information

7. **Loading Overlay**
   - Doctor animation (stethoscope)
   - Status message that changes every 1.5 seconds
   - Progress bar with optimized animation
   - Semi-transparent background

#### Animations & Interactions

1. **Header Animations**
   - Logo pulse effect
   - Title fade-in from top
   - Subtitle fade-in from bottom

2. **Tab Switching**
   - Active tab indicator slides horizontally
   - Content fades in when tab is selected

3. **Audio Recording**
   - Microphone button pulses when recording
   - Audio visualizer bars animate based on recording state
   - Buttons enable/disable based on recording state

4. **Image Upload**
   - Drag area highlights when file is dragged over
   - Smooth transition to preview mode when image is uploaded
   - Preview image scales to fit container

5. **Loading Animation**
   - Overlay fades in/out smoothly
   - Stethoscope rotates continuously
   - Progress bar fills with optimized timing (fast at start, slower at end)
   - Status messages change with fade transition

6. **Card Interactions**
   - Cards have subtle hover effect (elevation and scale)
   - Content areas expand to fit content
   - Scrollbars appear only when needed

7. **Responsive Behavior**
   - Fluid layout adjusts to screen size
   - Two-column layout on desktop becomes single-column on mobile
   - Font sizes and spacing adjust proportionally
   - Touch-friendly targets on mobile

### Backend

#### Framework & Architecture
- **Framework**: Flask (Python)
- **Architecture**: Monolithic application with modular components
- **API Style**: RESTful API endpoints

#### Core Modules

1. **Main Application (`app.py`)**
   - Flask application setup
   - Route definitions
   - Request handling
   - File upload management
   - Error handling

2. **Brain of the Doctor (`brain_of_the_doctor.py`)**
   - Image encoding and optimization
   - Integration with GROQ API
   - Model selection and fallback logic
   - Response generation

3. **Voice of the Patient (`voice_of_the_patient.py`)**
   - Audio transcription using GROQ API
   - Speech-to-text processing
   - Error handling for transcription

4. **Voice of the Doctor (`voice_of_the_doctor.py`)**
   - Text-to-speech conversion using Google TTS
   - Audio file generation and optimization
   - Error handling for audio generation

#### API Endpoints

1. **`/`** (GET)
   - Serves the main application interface
   - Returns the HTML template

2. **`/api/upload`** (POST)
   - Handles file uploads (audio and image)
   - Processes the files through the pipeline:
     1. Transcribes audio to text
     2. Analyzes image with the transcribed query
     3. Generates audio response from the diagnosis
   - Returns JSON with transcription, diagnosis, and audio file path

3. **`/uploads/<filename>`** (GET)
   - Serves uploaded and generated files
   - Used for accessing audio responses

#### External API Integrations

1. **GROQ API**
   - Used for:
     - Speech-to-text transcription
     - Image analysis with multimodal models
   - Models used:
     - `whisper-large-v3` for transcription (fallback to `whisper-small`)
     - `llama-3.1-8b-instant` for fast image analysis
     - Fallback chain of models for reliability

2. **Google Text-to-Speech API**
   - Used for generating audio responses
   - Configured for natural-sounding speech

### Database

The application uses a file-based storage system rather than a traditional database:

1. **File Storage Structure**
   - `/uploads/` directory for all user-uploaded and generated files
   - Unique UUID-based filenames to prevent collisions
   - Temporary storage (files not persisted long-term)

2. **File Types**
   - User-uploaded audio recordings (WAV format)
   - User-uploaded images (JPEG, PNG, etc.)
   - Generated audio responses (MP3 format)

3. **Data Flow**
   - Files are uploaded to temporary storage
   - Processed by the application
   - Results stored in the same directory
   - Paths to result files returned to the frontend

## Feature Specifications

### 1. Voice Recording & Transcription

**User Flow:**
1. User clicks the microphone button or "Start" button
2. Browser requests microphone permission (if not already granted)
3. Recording starts with visual feedback (pulsing button and animated visualizer)
4. User speaks their question about the medical image
5. User clicks "Stop" button to end recording
6. Recording is available for playback via "Play" button
7. When diagnosis is requested, the recording is sent to the server
8. Server transcribes the audio to text using GROQ API
9. Transcribed text is displayed in the output section

**Technical Requirements:**
- Use MediaRecorder API for audio capture
- Store audio in WAV format
- Implement visualizer using audio analysis
- Handle microphone permission requests and errors
- Provide clear feedback during recording process

### 2. Image Upload & Preview

**User Flow:**
1. User drags and drops an image or clicks "Select Image" button
2. File browser opens (if button was clicked)
3. User selects a medical image
4. Image is previewed in the interface
5. When diagnosis is requested, the image is sent to the server
6. Server processes the image for analysis

**Technical Requirements:**
- Support common image formats (JPEG, PNG, GIF, WebP)
- Implement drag and drop with visual feedback
- Optimize image preview for responsive display
- Validate file type and provide error messages if invalid
- Limit file size to reasonable limits (e.g., 5MB)

### 3. Medical Image Analysis

**User Flow:**
1. After uploading an image and recording a question, user clicks "Get Diagnosis"
2. Loading overlay appears with animations and status messages
3. Server analyzes the image using the transcribed question as context
4. AI generates a medical assessment based on the image
5. Diagnosis is displayed in the output section

**Technical Requirements:**
- Optimize image before sending to AI model
- Use GROQ API with vision-capable models
- Implement model fallback chain for reliability
- Structure the prompt to generate professional medical responses
- Format the response for readability

### 4. Text-to-Speech Response

**User Flow:**
1. After diagnosis is generated, server converts the text to speech
2. Audio file is generated and sent to the client
3. Audio player is populated with the response
4. User can play, pause, and control the audio playback

**Technical Requirements:**
- Use Google TTS for natural-sounding speech
- Optimize audio file size and quality
- Support proper playback in all major browsers
- Provide accessible audio controls

### 5. Responsive UI & Animations

**User Flow:**
1. Interface adapts to user's device screen size
2. Animations provide feedback for user actions
3. Loading states indicate processing is happening
4. Transitions between states are smooth and professional

**Technical Requirements:**
- Implement responsive design using CSS media queries
- Use CSS animations and transitions for visual effects
- Optimize animations for performance
- Ensure accessibility is maintained with animations

### 6. Error Handling & Recovery

**User Flow:**
1. If an error occurs, user receives a helpful message
2. Application remains functional even if one component fails
3. Clear instructions for recovery are provided

**Technical Requirements:**
- Implement comprehensive error handling on frontend and backend
- Provide user-friendly error messages
- Log detailed errors on the server for debugging
- Implement fallbacks for critical features

## Performance Requirements

1. **Response Time**
   - Diagnosis generation: 5-30 seconds
   - UI interactions: < 100ms
   - Page load: < 2 seconds

2. **Optimization**
   - Optimize images before processing
   - Use efficient models for faster response
   - Implement perception techniques to make wait times feel shorter

3. **Reliability**
   - Implement fallback mechanisms for all external API calls
   - Handle network errors gracefully
   - Provide meaningful feedback during processing

## Implementation Notes

1. **Frontend Structure**
   - `index.html`: Main application template
   - `static/css/styles.css`: All styles and animations
   - `static/js/main.js`: Frontend interactivity and API calls

2. **Backend Structure**
   - `app.py`: Main Flask application
   - `brain_of_the_doctor.py`: Image analysis logic
   - `voice_of_the_patient.py`: Speech-to-text logic
   - `voice_of_the_doctor.py`: Text-to-speech logic

3. **Deployment Considerations**
   - Environment variables for API keys
   - Temporary file storage management
   - CORS configuration for API access

## Security Considerations

1. **API Key Management**
   - Store API keys in environment variables
   - Never expose keys in frontend code

2. **File Upload Security**
   - Validate file types and sizes
   - Generate random filenames to prevent path traversal
   - Implement proper file permissions

3. **Data Privacy**
   - Do not store user data permanently
   - Clear temporary files periodically
   - Provide clear privacy information to users

---

This masterplan provides a comprehensive blueprint for recreating the Arogya Doctor Vision application with complete fidelity to the original design and functionality. Follow these specifications carefully to ensure an exact recreation of the application.
