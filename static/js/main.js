/**
 * Main JavaScript for Crawl4AI Web Application
 */

// Global variables
let currentTaskId = null;
let currentTaskData = null;

// DOM elements
const crawlForm = document.getElementById('crawl-form');
const urlInput = document.getElementById('url');
const extractionStrategy = document.getElementById('extraction-strategy');
const wordThreshold = document.getElementById('word-threshold');
const wordThresholdValue = document.getElementById('word-threshold-value');
const cssSelector = document.getElementById('css-selector');
const cssSelectorGroup = document.getElementById('css-selector-group');
const screenshot = document.getElementById('screenshot');
const removeOverlays = document.getElementById('remove-overlays');
const excludeExternal = document.getElementById('exclude-external');

const startCrawlBtn = document.getElementById('start-crawl-btn');
const stopCrawlBtn = document.getElementById('stop-crawl-btn');

const progressSection = document.getElementById('progress-section');
const progressBar = document.getElementById('progress-bar');
const progressText = document.getElementById('progress-text');
const progressPercentage = document.getElementById('progress-percentage');

const welcomeMessage = document.getElementById('welcome-message');
const resultsContent = document.getElementById('results-content');
const errorMessage = document.getElementById('error-message');
const errorText = document.getElementById('error-text');

const resultTabs = document.querySelectorAll('input[name="result-view"]');
const markdownContent = document.getElementById('markdown-content');
const htmlContent = document.getElementById('html-content');
const jsonContent = document.getElementById('json-content');

const markdownText = document.getElementById('markdown-text');
const htmlText = document.getElementById('html-text');
const jsonText = document.getElementById('json-text');

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    initializeWebSocket();
    loadSavedSettings();
});

function initializeEventListeners() {
    // Form submission
    crawlForm.addEventListener('submit', handleFormSubmit);
    
    // Stop crawling
    stopCrawlBtn.addEventListener('click', handleStopCrawl);
    
    // Word threshold slider
    wordThreshold.addEventListener('input', function() {
        wordThresholdValue.textContent = this.value;
    });
    
    // Extraction strategy change
    extractionStrategy.addEventListener('change', function() {
        if (this.value === 'css') {
            cssSelectorGroup.style.display = 'block';
            cssSelector.required = true;
        } else {
            cssSelectorGroup.style.display = 'none';
            cssSelector.required = false;
        }
    });
    
    // Result view tabs
    resultTabs.forEach(tab => {
        tab.addEventListener('change', function() {
            showResultView(this.id.replace('-tab', ''));
        });
    });
    
    // URL input validation
    urlInput.addEventListener('input', validateUrl);
    urlInput.addEventListener('blur', validateUrl);
}

function initializeWebSocket() {
    if (window.wsManager) {
        // Set up WebSocket event handlers
        window.wsManager.onTaskUpdate = handleTaskUpdate;
        window.wsManager.onTaskCompleted = handleTaskCompleted;
        window.wsManager.onTaskError = handleTaskError;
    }
}

function loadSavedSettings() {
    // Load settings from localStorage
    const savedSettings = localStorage.getItem('crawl4ai-settings');
    if (savedSettings) {
        try {
            const settings = JSON.parse(savedSettings);
            
            if (settings.extractionStrategy) {
                extractionStrategy.value = settings.extractionStrategy;
                extractionStrategy.dispatchEvent(new Event('change'));
            }
            
            if (settings.wordThreshold) {
                wordThreshold.value = settings.wordThreshold;
                wordThresholdValue.textContent = settings.wordThreshold;
            }
            
            if (settings.cssSelector) {
                cssSelector.value = settings.cssSelector;
            }
            
            if (typeof settings.screenshot === 'boolean') {
                screenshot.checked = settings.screenshot;
            }
            
            if (typeof settings.removeOverlays === 'boolean') {
                removeOverlays.checked = settings.removeOverlays;
            }
            
            if (typeof settings.excludeExternal === 'boolean') {
                excludeExternal.checked = settings.excludeExternal;
            }
        } catch (error) {
            console.error('Error loading saved settings:', error);
        }
    }
}

function saveSettings() {
    const settings = {
        extractionStrategy: extractionStrategy.value,
        wordThreshold: wordThreshold.value,
        cssSelector: cssSelector.value,
        screenshot: screenshot.checked,
        removeOverlays: removeOverlays.checked,
        excludeExternal: excludeExternal.checked
    };
    
    localStorage.setItem('crawl4ai-settings', JSON.stringify(settings));
}

function validateUrl() {
    const url = urlInput.value.trim();
    
    if (!url) {
        urlInput.classList.remove('is-valid', 'is-invalid');
        return false;
    }
    
    try {
        const urlObj = new URL(url);
        if (urlObj.protocol === 'http:' || urlObj.protocol === 'https:') {
            urlInput.classList.remove('is-invalid');
            urlInput.classList.add('is-valid');
            return true;
        } else {
            throw new Error('Invalid protocol');
        }
    } catch (error) {
        urlInput.classList.remove('is-valid');
        urlInput.classList.add('is-invalid');
        return false;
    }
}

async function handleFormSubmit(event) {
    event.preventDefault();
    
    if (!validateUrl()) {
        showError('Please enter a valid HTTP or HTTPS URL');
        return;
    }
    
    // Save current settings
    saveSettings();
    
    // Prepare request data
    const requestData = {
        url: urlInput.value.trim(),
        config: {
            word_count_threshold: parseInt(wordThreshold.value),
            extraction_strategy: extractionStrategy.value,
            css_selector: extractionStrategy.value === 'css' ? cssSelector.value : null,
            screenshot: screenshot.checked,
            remove_overlay_elements: removeOverlays.checked,
            exclude_external_links: excludeExternal.checked,
            exclude_social_media_links: excludeExternal.checked,
            timeout: 60
        }
    };
    
    try {
        // Show loading state
        setLoadingState(true);
        hideError();
        hideResults();
        
        // Send request to API
        const response = await fetch('/api/v1/crawl', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to start crawling');
        }

        const taskData = await response.json();
        currentTaskId = taskData.task_id;
        currentTaskData = taskData;

        console.log('Crawl task created:', taskData);
        
        // Subscribe to task updates via WebSocket
        if (window.wsManager && window.wsManager.connected) {
            window.wsManager.subscribeToTask(currentTaskId);
        }
        
        // Start polling for updates (fallback)
        startPolling();
        
        // Update UI
        updateProgress(taskData.progress, 'Task created, starting crawl...');
        
    } catch (error) {
        console.error('Error starting crawl:', error);
        showError(error.message);
        setLoadingState(false);
    }
}

function handleStopCrawl() {
    if (currentTaskId) {
        fetch(`/api/v1/crawl/${currentTaskId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (response.ok) {
                setLoadingState(false);
                updateProgress(0, 'Crawl cancelled');
                
                // Unsubscribe from WebSocket updates
                if (window.wsManager) {
                    window.wsManager.unsubscribeFromTask(currentTaskId);
                }
                
                currentTaskId = null;
                currentTaskData = null;
            }
        })
        .catch(error => {
            console.error('Error cancelling crawl:', error);
        });
    }
}

function handleTaskUpdate(data) {
    if (data.task_id === currentTaskId) {
        updateProgress(data.progress, getProgressText(data.status, data.progress));
        
        // Update current task data
        if (currentTaskData) {
            currentTaskData.status = data.status;
            currentTaskData.progress = data.progress;
        }
    }
}

function handleTaskCompleted(data) {
    if (data.task_id === currentTaskId) {
        setLoadingState(false);
        updateProgress(1.0, 'Crawl completed successfully!');
        
        // Display results
        displayResults(data.result);
        
        // Unsubscribe from updates
        if (window.wsManager) {
            window.wsManager.unsubscribeFromTask(currentTaskId);
        }
    }
}

function handleTaskError(data) {
    if (data.task_id === currentTaskId) {
        setLoadingState(false);
        showError(data.error || 'An error occurred during crawling');
        
        // Unsubscribe from updates
        if (window.wsManager) {
            window.wsManager.unsubscribeFromTask(currentTaskId);
        }
        
        currentTaskId = null;
        currentTaskData = null;
    }
}

function startPolling() {
    if (!currentTaskId) return;
    
    const pollInterval = setInterval(async () => {
        if (!currentTaskId) {
            clearInterval(pollInterval);
            return;
        }
        
        try {
            const response = await fetch(`/api/v1/crawl/${currentTaskId}`);
            if (!response.ok) {
                throw new Error('Failed to get task status');
            }
            
            const taskData = await response.json();
            
            if (taskData.status === 'completed') {
                clearInterval(pollInterval);
                handleTaskCompleted({ task_id: currentTaskId, result: taskData.result });
            } else if (taskData.status === 'failed') {
                clearInterval(pollInterval);
                handleTaskError({ task_id: currentTaskId, error: taskData.error });
            } else {
                handleTaskUpdate({
                    task_id: currentTaskId,
                    status: taskData.status,
                    progress: taskData.progress
                });
            }
        } catch (error) {
            console.error('Error polling task status:', error);
        }
    }, 2000); // Poll every 2 seconds
}

function setLoadingState(loading) {
    startCrawlBtn.disabled = loading;
    stopCrawlBtn.disabled = !loading;
    
    if (loading) {
        startCrawlBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Crawling...';
        progressSection.style.display = 'block';
    } else {
        startCrawlBtn.innerHTML = '<i class="fas fa-play me-2"></i>Start Crawling';
        progressSection.style.display = 'none';
    }
}

function updateProgress(progress, text) {
    const percentage = Math.round(progress * 100);
    progressBar.style.width = `${percentage}%`;
    progressBar.setAttribute('aria-valuenow', percentage);
    progressText.textContent = text;
    progressPercentage.textContent = `${percentage}%`;
}

function getProgressText(status, progress) {
    switch (status) {
        case 'pending':
            return 'Initializing crawler...';
        case 'running':
            if (progress < 0.3) return 'Loading page...';
            if (progress < 0.8) return 'Extracting content...';
            return 'Processing results...';
        case 'completed':
            return 'Crawl completed successfully!';
        case 'failed':
            return 'Crawl failed';
        case 'cancelled':
            return 'Crawl cancelled';
        default:
            return 'Processing...';
    }
}

function displayResults(result) {
    welcomeMessage.style.display = 'none';
    resultsContent.style.display = 'block';

    // Populate result content
    markdownText.textContent = result.markdown || 'No markdown content available';
    htmlText.textContent = result.html || 'No HTML content available';
    jsonText.textContent = JSON.stringify(result, null, 2);

    // Show the currently selected view
    const selectedTab = document.querySelector('input[name="result-view"]:checked');
    if (selectedTab) {
        showResultView(selectedTab.id.replace('-tab', ''));
    }

    // Show success message
    console.log('Results displayed successfully');

    // Update current task data with result
    if (currentTaskData) {
        currentTaskData.result = result;
    }
}

function showResultView(viewType) {
    // Hide all views
    document.querySelectorAll('.result-view').forEach(view => {
        view.style.display = 'none';
    });
    
    // Show selected view
    const targetView = document.getElementById(`${viewType}-content`);
    if (targetView) {
        targetView.style.display = 'block';
    }
}

function hideResults() {
    resultsContent.style.display = 'none';
    welcomeMessage.style.display = 'block';
}

function showError(message) {
    errorText.textContent = message;
    errorMessage.style.display = 'block';
}

function hideError() {
    errorMessage.style.display = 'none';
}

// Utility functions
function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        navigator.clipboard.writeText(element.textContent)
            .then(() => {
                // Show success feedback
                const btn = event.target.closest('button');
                const originalText = btn.innerHTML;
                btn.innerHTML = '<i class="fas fa-check me-1"></i>Copied!';
                btn.classList.add('btn-success');
                btn.classList.remove('btn-outline-secondary');
                
                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.classList.remove('btn-success');
                    btn.classList.add('btn-outline-secondary');
                }, 2000);
            })
            .catch(err => {
                console.error('Failed to copy text: ', err);
            });
    }
}

function downloadResult(format) {
    if (!currentTaskData || !currentTaskData.result) {
        return;
    }
    
    let content, filename, mimeType;
    
    switch (format) {
        case 'markdown':
            content = currentTaskData.result.markdown || '';
            filename = 'crawl-result.md';
            mimeType = 'text/markdown';
            break;
        case 'html':
            content = currentTaskData.result.html || '';
            filename = 'crawl-result.html';
            mimeType = 'text/html';
            break;
        case 'json':
            content = JSON.stringify(currentTaskData.result, null, 2);
            filename = 'crawl-result.json';
            mimeType = 'application/json';
            break;
        default:
            return;
    }
    
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
