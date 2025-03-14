/**
 * WebToys Laboratory - Main frontend JavaScript
 * This script manages the experimental laboratory interface
 */

// State management
const state = {
    description: '',
    isGenerating: false,
    previewId: null,
    webToyCode: null,
    errorMessage: null,
    currentView: 'create', // 'create', 'preview', 'share'
    generationPhase: 0, // 0-100 to track generation progress
    generationTimer: null // For simulating progress updates
  };
  
  // DOM Elements
  let descriptionInput, generateButton, previewFrame, publishButton, 
      regenerateButton, shareLink, errorDisplay, loadingIndicator,
      viewWebToyButton, copyLinkButton, copySuccess,
      progressBar, progressText, progressStatus;
  
  // Initialize the application
  function initApp() {
    // Get DOM elements
    descriptionInput = document.getElementById('description-input');
    generateButton = document.getElementById('generate-button');
    previewFrame = document.getElementById('preview-frame');
    publishButton = document.getElementById('publish-button');
    regenerateButton = document.getElementById('regenerate-button');
    shareLink = document.getElementById('share-link');
    viewWebToyButton = document.getElementById('view-webtoy-button');
    copyLinkButton = document.getElementById('copy-link-button');
    copySuccess = document.getElementById('copy-success');
    errorDisplay = document.getElementById('error-display');
    loadingIndicator = document.getElementById('loading-indicator');
    progressBar = document.getElementById('progress-bar');
    progressText = document.getElementById('progress-text');
    progressStatus = document.getElementById('progress-status');
    
    // Hide sections initially
    document.getElementById('preview-section').style.display = 'none';
    document.getElementById('share-section').style.display = 'none';
    errorDisplay.style.display = 'none';
    loadingIndicator.style.display = 'none';
    
    // Add event listeners
    generateButton.addEventListener('click', handleGenerate);
    publishButton.addEventListener('click', handlePublish);
    regenerateButton.addEventListener('click', handleRegenerate);
    copyLinkButton.addEventListener('click', handleCopyLink);
    descriptionInput.addEventListener('input', validateInput);
    
    // Setup example prompts as clickable
    setupExamplePrompts();
    
    // Initial button state
    validateInput();
  }
  
  // Validate input and update button state
  function validateInput() {
    state.description = descriptionInput.value.trim();
    generateButton.disabled = state.description.length < 10 || state.isGenerating;
  }
  
  // Setup example prompts as clickable
  function setupExamplePrompts() {
    const examples = document.querySelectorAll('.examples li');
    examples.forEach(example => {
      example.addEventListener('click', () => {
        descriptionInput.value = example.textContent;
        validateInput();
        descriptionInput.focus();
      });
    });
  }
  
  // Handle WebToy generation
  async function handleGenerate() {
    // Update UI state
    state.isGenerating = true;
    state.errorMessage = null;
    state.generationPhase = 0;
    errorDisplay.style.display = 'none';
    loadingIndicator.style.display = 'flex';
    generateButton.disabled = true;
    
    // Reset progress elements
    progressBar.style.width = '0%';
    progressText.textContent = 'Initializing experiment...';
    progressStatus.innerHTML = `
      <p class="status-line">$ initializing_laboratory...</p>
      <p class="status-line">$ connecting_to_ai_model...</p>
      <p class="status-line blink">$ _</p>
    `;
    
    // Start simulated progress updates
    startProgressSimulation();
    
    try {
        // Add initial simulation steps before API call
        await simulateProgressStep('analyzing_description', 1000);
        await simulateProgressStep('preparing_canvas_environment', 800);
        await simulateProgressStep('optimizing_parameters', 700);
        
        // Call the API
        updateProgressStatus('sending_request_to_ai_model...');
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                description: state.description,
                parameters: {
                    width: 500,
                    height: 500,
                    complexity: "medium",
                    style: "modern"
                }
            })
        });
        
        // After API call starts, add more simulation steps
        updateProgressStatus('ai_model_processing...');
        updateProgress(30);
        
        // Parse JSON even for error responses to get detailed error message
        await simulateProgressStep('generating_code_structure', 1200);
        await simulateProgressStep('implementing_canvas_logic', 1000);
        await simulateProgressStep('optimizing_performance', 800);
        const data = await response.json();
        
        // Handle API response
        if (!response.ok) {
            // If we have detailed validation errors, show them
            if (data.issues && Array.isArray(data.issues)) {
                throw new Error(
                    `Failed to generate WebToy: ${data.detail || ''}\n` +
                    data.issues.map(issue => `• ${issue}`).join('\n')
                );
            } else {
                throw new Error(data.detail || 'Failed to generate WebToy');
            }
        }
        
        // Update state with results
        state.previewId = data.preview_id;
        state.webToyCode = data.code;
        
        // Complete the progress
        await simulateProgressStep('finalizing_experiment', 500);
        await simulateProgressStep('preparing_preview_environment', 700);
        updateProgress(100);
        updateProgressStatus('experiment_ready!');
        
        // Brief pause to show 100% complete
        await new Promise(resolve => setTimeout(resolve, 800));
        
        // Show preview
        showPreview();
        
    } catch (error) {
        // Stop the progress simulation
        stopProgressSimulation();
        
        // Display error
        updateProgressStatus(`error: ${error.message}`);
        state.errorMessage = error.message;
        errorDisplay.innerHTML = state.errorMessage.replace(/\n/g, '<br>');
        errorDisplay.style.display = 'block';
    } finally {
        // Reset UI state
        state.isGenerating = false;
        loadingIndicator.style.display = 'none';
        validateInput();
    }
  }
  
  // Start the progress simulation
  function startProgressSimulation() {
    if (state.generationTimer) {
      clearInterval(state.generationTimer);
    }
    
    // Slowly increase progress if it gets stuck
    state.generationTimer = setInterval(() => {
      if (state.generationPhase < 90) {
        state.generationPhase += 0.5;
        progressBar.style.width = `${state.generationPhase}%`;
        
        // Add random "computing" messages every few seconds
        if (Math.random() < 0.1) {
          const messages = [
            'analyzing_visual_patterns...',
            'optimizing_render_pipeline...',
            'calculating_interactions...',
            'enhancing_user_experience...',
            'fine_tuning_animations...',
            'performing_code_quality_checks...'
          ];
          const randomMessage = messages[Math.floor(Math.random() * messages.length)];
          updateProgressStatus(randomMessage);
        }
      }
    }, 500);
  }
  
  // Stop the progress simulation
  function stopProgressSimulation() {
    if (state.generationTimer) {
      clearInterval(state.generationTimer);
      state.generationTimer = null;
    }
  }
  
  // Update the progress bar
  function updateProgress(percent) {
    state.generationPhase = percent;
    progressBar.style.width = `${percent}%`;
    
    if (percent < 30) {
      progressText.textContent = 'Analyzing experiment parameters...';
    } else if (percent < 60) {
      progressText.textContent = 'Generating code constructs...';
    } else if (percent < 90) {
      progressText.textContent = 'Optimizing and finalizing experiment...';
    } else {
      progressText.textContent = 'Experiment ready!';
    }
  }
  
  // Update the progress status with a new line
  function updateProgressStatus(message) {
    const lines = progressStatus.querySelectorAll('.status-line');
    const lastLine = lines[lines.length - 1];
    
    // Remove the blinking cursor from the last line
    if (lastLine) {
      lastLine.classList.remove('blink');
      if (lastLine.textContent.endsWith('_')) {
        lastLine.textContent = lastLine.textContent.slice(0, -1);
      }
    }
    
    // Add the new line with blinking cursor
    const newLine = document.createElement('p');
    newLine.classList.add('status-line', 'blink');
    newLine.textContent = `$ ${message}_`;
    progressStatus.appendChild(newLine);
    
    // Scroll to the bottom
    progressStatus.scrollTop = progressStatus.scrollHeight;
    
    // Remove older lines if there are too many
    const allLines = progressStatus.querySelectorAll('.status-line');
    if (allLines.length > 15) {
      progressStatus.removeChild(allLines[0]);
    }
  }
  
  // Simulate a progress step with a delay
  async function simulateProgressStep(message, delay) {
    updateProgressStatus(message);
    await new Promise(resolve => setTimeout(resolve, delay));
    updateProgress(Math.min(state.generationPhase + 10, 90));
  }
  
  // Show WebToy preview
  function showPreview() {
    // Update view state
    state.currentView = 'preview';
    
    // Show preview section, hide others
    document.getElementById('create-section').style.display = 'none';
    document.getElementById('preview-section').style.display = 'block';
    document.getElementById('share-section').style.display = 'none';
    
    // Set iframe source
    if (state.previewId) {
      previewFrame.src = `/preview/${state.previewId}`;
    } else if (state.webToyCode) {
      // Create sandbox and load code directly
      const container = document.querySelector('.iframe-container');
      const sandbox = new WebToySandbox('.iframe-container');
      sandbox.loadWebToy(state.webToyCode, { title: 'WebToy Preview' });
    }
    
    // Scroll to preview
    document.getElementById('preview-section').scrollIntoView({ behavior: 'smooth' });
  }
  
  // Handle regeneration request
  function handleRegenerate() {
    // Stop any ongoing progress simulation
    stopProgressSimulation();
    
    // Reset to create view
    state.currentView = 'create';
    state.generationPhase = 0;
    document.getElementById('create-section').style.display = 'block';
    document.getElementById('preview-section').style.display = 'none';
    document.getElementById('share-section').style.display = 'none';
    
    // Scroll back to the form
    document.getElementById('create-section').scrollIntoView({ behavior: 'smooth' });
  }
  
  // Handle publish request
  async function handlePublish() {
    if (!state.previewId) return;
    
    // Reset and show loading indicator with different message
    loadingIndicator.style.display = 'flex';
    progressBar.style.width = '0%';
    progressText.textContent = 'Preparing to publish experiment...';
    progressStatus.innerHTML = `
      <p class="status-line">$ initializing_publish_sequence...</p>
      <p class="status-line blink">$ _</p>
    `;
    publishButton.disabled = true;
    
    // Start simulated progress for publishing
    startProgressSimulation();
    
    try {
      // Add publishing simulation steps
      await simulateProgressStep('validating_experiment_data', 800);
      await simulateProgressStep('preparing_storage_environment', 700);
      
      // Make the API call
      updateProgressStatus('sending_publish_request...');
      const response = await fetch('/api/publish', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          preview_id: state.previewId
        })
      });
      
      // Continue with publishing simulation
      await simulateProgressStep('creating_permanent_record', 900);
      await simulateProgressStep('generating_public_url', 800);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to publish WebToy');
      }
      
      const data = await response.json();
      
      // Complete the progress animation
      await simulateProgressStep('finalizing_publication', 600);
      updateProgress(100);
      updateProgressStatus('publication_complete!');
      
      // Brief pause to show 100% complete
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Show share section
      state.currentView = 'share';
      document.getElementById('preview-section').style.display = 'none';
      document.getElementById('share-section').style.display = 'block';
      
      // Update share link
      const fullUrl = data.url;
      shareLink.textContent = fullUrl;
      shareLink.href = fullUrl;
      
      // Update view button
      viewWebToyButton.href = fullUrl;
      
    } catch (error) {
      // Stop the progress simulation
      stopProgressSimulation();
      
      // Display error
      updateProgressStatus(`error: ${error.message}`);
      state.errorMessage = error.message;
      errorDisplay.textContent = state.errorMessage;
      errorDisplay.style.display = 'block';
    } finally {
      // Reset UI state
      stopProgressSimulation();
      loadingIndicator.style.display = 'none';
      publishButton.disabled = false;
    }
  }
  
  // Handle copy link button
  function handleCopyLink() {
    if (!shareLink.textContent) return;
    
    navigator.clipboard.writeText(shareLink.textContent)
      .then(() => {
        // Show success message with animation
        copySuccess.style.display = 'inline';
        copySuccess.textContent = 'Copied to clipboard!';
        
        // Add typing effect
        let messageText = 'Copied to clipboard!';
        copySuccess.textContent = '';
        let i = 0;
        
        const typeWriter = () => {
          if (i < messageText.length) {
            copySuccess.textContent += messageText.charAt(i);
            i++;
            setTimeout(typeWriter, 50);
          }
        };
        
        typeWriter();
        
        // Hide after delay
        setTimeout(() => {
          copySuccess.style.display = 'none';
        }, 3000);
      })
      .catch(error => {
        console.error('Failed to copy link: ', error);
        copySuccess.textContent = 'Error copying link';
        copySuccess.style.display = 'inline';
        
        setTimeout(() => {
          copySuccess.style.display = 'none';
        }, 3000);
      });
  }
  
  // Initialize the app when DOM is ready
  document.addEventListener('DOMContentLoaded', initApp);