/**
 * WebToys App - Main frontend JavaScript
 */

// State management
const state = {
    description: '',
    isGenerating: false,
    previewId: null,
    webToyCode: null,
    errorMessage: null,
    currentView: 'create' // 'create', 'preview', 'share'
  };
  
  // DOM Elements
  let descriptionInput, generateButton, previewFrame, publishButton, 
      regenerateButton, shareLink, errorDisplay, loadingIndicator,
      viewWebToyButton, copyLinkButton, copySuccess;
  
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
    errorDisplay.style.display = 'none';
    loadingIndicator.style.display = 'flex';
    generateButton.disabled = true;
    
    try {
      // Call the API
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          description: state.description
        })
      });
      
      // Handle API response
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate WebToy');
      }
      
      const data = await response.json();
      
      // Update state with results
      state.previewId = data.preview_id;
      state.webToyCode = data.code;
      
      // Show preview
      showPreview();
      
    } catch (error) {
      // Display error
      state.errorMessage = error.message;
      errorDisplay.textContent = state.errorMessage;
      errorDisplay.style.display = 'block';
    } finally {
      // Reset UI state
      state.isGenerating = false;
      loadingIndicator.style.display = 'none';
      validateInput();
    }
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
    // Reset to create view
    state.currentView = 'create';
    document.getElementById('create-section').style.display = 'block';
    document.getElementById('preview-section').style.display = 'none';
    document.getElementById('share-section').style.display = 'none';
  }
  
  // Handle publish request
  async function handlePublish() {
    if (!state.previewId) return;
    
    loadingIndicator.style.display = 'flex';
    publishButton.disabled = true;
    
    try {
      const response = await fetch('/api/publish', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          preview_id: state.previewId
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to publish WebToy');
      }
      
      const data = await response.json();
      
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
      // Display error
      state.errorMessage = error.message;
      errorDisplay.textContent = state.errorMessage;
      errorDisplay.style.display = 'block';
    } finally {
      // Reset UI state
      loadingIndicator.style.display = 'none';
      publishButton.disabled = false;
    }
  }
  
  // Handle copy link button
  function handleCopyLink() {
    if (!shareLink.textContent) return;
    
    navigator.clipboard.writeText(shareLink.textContent)
      .then(() => {
        copySuccess.style.display = 'inline';
        setTimeout(() => {
          copySuccess.style.display = 'none';
        }, 2000);
      })
      .catch(error => {
        console.error('Failed to copy link: ', error);
      });
  }
  
  // Initialize the app when DOM is ready
  document.addEventListener('DOMContentLoaded', initApp);