// Global variables
let uploadedProjects = JSON.parse(localStorage.getItem('uploadedProjects')) || [];
let uploadedFiles = [];

// DOM elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const uploadProgress = document.getElementById('uploadProgress');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const projectsGrid = document.getElementById('projectsGrid');
const filterBtns = document.querySelectorAll('.filter-btn');
const modal = document.getElementById('projectModal');
const modalTitle = document.getElementById('modalTitle');
const projectPreview = document.getElementById('projectPreview');
const closeModal = document.querySelector('.close');
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    renderProjects();
    addSampleProjects();
});

// Initialize all event listeners
function initializeEventListeners() {
    // Mobile navigation
    hamburger.addEventListener('click', () => {
        navMenu.classList.toggle('active');
    });

    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                navMenu.classList.remove('active');
            }
        });
    });

    // File upload events
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    fileInput.addEventListener('change', handleFileSelect);
    uploadBtn.addEventListener('click', handleUpload);

    // Filter buttons
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterProjects(btn.dataset.filter);
        });
    });

    // Modal events
    closeModal.addEventListener('click', closeProjectModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeProjectModal();
    });

    // Download and share buttons
    document.getElementById('downloadBtn').addEventListener('click', downloadProject);
    document.getElementById('shareBtn').addEventListener('click', shareProject);
}

// Drag and drop handlers
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = Array.from(e.dataTransfer.files);
    processFiles(files);
}

function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    processFiles(files);
}

// Process selected files
function processFiles(files) {
    uploadedFiles = files;
    updateUploadAreaDisplay();
}

function updateUploadAreaDisplay() {
    const uploadContent = document.querySelector('.upload-content');
    if (uploadedFiles.length > 0) {
        uploadContent.innerHTML = `
            <i class="fas fa-check-circle upload-icon" style="color: #10b981;"></i>
            <h3>${uploadedFiles.length} file(s) selected</h3>
            <p>${uploadedFiles.map(f => f.name).join(', ')}</p>
        `;
    } else {
        uploadContent.innerHTML = `
            <i class="fas fa-cloud-upload-alt upload-icon"></i>
            <h3>Drop files here or click to upload</h3>
            <p>Supports: .ipynb, .py, .js, .html, .css, .md, .zip</p>
        `;
    }
}

// Handle project upload
async function handleUpload() {
    const title = document.getElementById('projectTitle').value.trim();
    const description = document.getElementById('projectDescription').value.trim();
    const tags = document.getElementById('projectTags').value.trim();

    if (!title) {
        alert('Please enter a project title');
        return;
    }

    if (uploadedFiles.length === 0) {
        alert('Please select files to upload');
        return;
    }

    // Show progress
    uploadProgress.style.display = 'block';
    simulateUpload();

    // Create project object
    const project = {
        id: Date.now(),
        title,
        description: description || 'No description provided',
        tags: tags.split(',').map(tag => tag.trim()).filter(tag => tag),
        files: await processProjectFiles(uploadedFiles),
        uploadDate: new Date().toISOString(),
        type: determineProjectType(uploadedFiles, tags)
    };

    // Save project
    uploadedProjects.push(project);
    localStorage.setItem('uploadedProjects', JSON.stringify(uploadedProjects));

    // Reset form
    setTimeout(() => {
        resetUploadForm();
        renderProjects();
        alert('Project uploaded successfully!');
    }, 2000);
}

// Simulate upload progress
function simulateUpload() {
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress >= 100) {
            progress = 100;
            clearInterval(interval);
        }
        progressFill.style.width = progress + '%';
        progressText.textContent = `Uploading... ${Math.round(progress)}%`;
    }, 200);
}

// Process project files
async function processProjectFiles(files) {
    const processedFiles = [];
    
    for (const file of files) {
        const fileData = {
            name: file.name,
            size: file.size,
            type: file.type,
            content: await readFileContent(file)
        };
        processedFiles.push(fileData);
    }
    
    return processedFiles;
}

// Read file content
function readFileContent(file) {
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            resolve(e.target.result);
        };
        
        if (file.name.endsWith('.ipynb') || file.name.endsWith('.json') || 
            file.name.endsWith('.py') || file.name.endsWith('.js') || 
            file.name.endsWith('.html') || file.name.endsWith('.css') || 
            file.name.endsWith('.md')) {
            reader.readAsText(file);
        } else {
            reader.readAsDataURL(file);
        }
    });
}

// Determine project type
function determineProjectType(files, tags) {
    const fileNames = files.map(f => f.name.toLowerCase());
    const tagString = tags.toLowerCase();
    
    if (fileNames.some(name => name.endsWith('.ipynb')) || tagString.includes('data-science') || tagString.includes('machine-learning')) {
        return 'data-science';
    } else if (fileNames.some(name => name.endsWith('.py')) || tagString.includes('python')) {
        return 'python';
    } else if (fileNames.some(name => name.endsWith('.js') || name.endsWith('.html') || name.endsWith('.css')) || tagString.includes('web')) {
        return 'web-dev';
    } else if (tagString.includes('javascript') || tagString.includes('js')) {
        return 'javascript';
    }
    
    return 'other';
}

// Reset upload form
function resetUploadForm() {
    document.getElementById('projectTitle').value = '';
    document.getElementById('projectDescription').value = '';
    document.getElementById('projectTags').value = '';
    uploadedFiles = [];
    updateUploadAreaDisplay();
    uploadProgress.style.display = 'none';
    progressFill.style.width = '0%';
}

// Add sample projects for demonstration
function addSampleProjects() {
    if (uploadedProjects.length === 0) {
        const sampleProjects = [
            {
                id: 1,
                title: 'Machine Learning Classification',
                description: 'A comprehensive machine learning project using SVM for classification tasks with data visualization.',
                tags: ['python', 'machine-learning', 'sklearn', 'data-science'],
                files: [
                    {
                        name: 'svm_classifier.ipynb',
                        type: 'application/json',
                        content: '{"cells": [{"cell_type": "markdown", "source": ["# SVM Classification Project\\n\\nThis notebook demonstrates Support Vector Machine classification."]}, {"cell_type": "code", "source": ["import numpy as np\\nimport pandas as pd\\nfrom sklearn import svm\\nimport matplotlib.pyplot as plt\\n\\n# Load data\\ndata = pd.read_csv(\'data.csv\')\\nprint(data.head())"], "execution_count": null, "outputs": []}]}'
                    }
                ],
                uploadDate: new Date('2024-01-15').toISOString(),
                type: 'data-science'
            },
            {
                id: 2,
                title: 'React Todo App',
                description: 'A modern todo application built with React, featuring drag-and-drop functionality and local storage.',
                tags: ['react', 'javascript', 'web-dev', 'frontend'],
                files: [
                    {
                        name: 'App.js',
                        type: 'text/javascript',
                        content: 'import React, { useState } from "react";\n\nfunction App() {\n  const [todos, setTodos] = useState([]);\n  \n  return (\n    <div className="App">\n      <h1>Todo App</h1>\n      {/* Todo implementation */}\n    </div>\n  );\n}\n\nexport default App;'
                    }
                ],
                uploadDate: new Date('2024-01-20').toISOString(),
                type: 'web-dev'
            },
            {
                id: 3,
                title: 'Data Visualization Dashboard',
                description: 'Interactive dashboard for visualizing sales data with charts and filters using Python and Plotly.',
                tags: ['python', 'plotly', 'dashboard', 'data-visualization'],
                files: [
                    {
                        name: 'dashboard.py',
                        type: 'text/x-python',
                        content: 'import plotly.dash as dash\nimport plotly.express as px\nimport pandas as pd\n\n# Create dashboard\napp = dash.Dash(__name__)\n\n# Load data\ndf = pd.read_csv("sales_data.csv")\n\n# Create visualizations\nfig = px.bar(df, x="month", y="sales")\n\nif __name__ == "__main__":\n    app.run_server(debug=True)'
                    }
                ],
                uploadDate: new Date('2024-01-25').toISOString(),
                type: 'python'
            }
        ];
        
        uploadedProjects = sampleProjects;
        localStorage.setItem('uploadedProjects', JSON.stringify(uploadedProjects));
    }
}

// Render projects in gallery
function renderProjects(filter = 'all') {
    const filteredProjects = filter === 'all' 
        ? uploadedProjects 
        : uploadedProjects.filter(project => project.type === filter);

    projectsGrid.innerHTML = filteredProjects.map(project => `
        <div class="project-card" onclick="openProjectModal(${project.id})">
            <div class="project-image">
                <i class="fas ${getProjectIcon(project.type)}"></i>
            </div>
            <div class="project-info">
                <h3 class="project-title">${project.title}</h3>
                <p class="project-description">${project.description}</p>
                <div class="project-tags">
                    ${project.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                </div>
                <div class="project-meta">
                    <span><i class="fas fa-calendar"></i> ${formatDate(project.uploadDate)}</span>
                    <span><i class="fas fa-file"></i> ${project.files.length} files</span>
                </div>
            </div>
        </div>
    `).join('');
}

// Get project icon based on type
function getProjectIcon(type) {
    const icons = {
        'data-science': 'fa-chart-line',
        'python': 'fa-python',
        'web-dev': 'fa-code',
        'javascript': 'fa-js-square',
        'other': 'fa-file-code'
    };
    return icons[type] || icons.other;
}

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

// Filter projects
function filterProjects(filter) {
    renderProjects(filter);
}

// Open project modal
function openProjectModal(projectId) {
    const project = uploadedProjects.find(p => p.id === projectId);
    if (!project) return;

    modalTitle.textContent = project.title;
    
    // Display project files
    const filesHTML = project.files.map(file => {
        if (file.name.endsWith('.ipynb')) {
            return renderJupyterNotebook(file);
        } else if (file.name.endsWith('.py') || file.name.endsWith('.js') || 
                   file.name.endsWith('.html') || file.name.endsWith('.css') || 
                   file.name.endsWith('.md')) {
            return renderCodeFile(file);
        } else {
            return renderGenericFile(file);
        }
    }).join('');

    projectPreview.innerHTML = `
        <div class="project-details">
            <p><strong>Description:</strong> ${project.description}</p>
            <p><strong>Tags:</strong> ${project.tags.join(', ')}</p>
            <p><strong>Uploaded:</strong> ${formatDate(project.uploadDate)}</p>
            <hr style="margin: 1rem 0; border: none; border-top: 1px solid #e5e7eb;">
        </div>
        ${filesHTML}
    `;

    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

// Render Jupyter notebook
function renderJupyterNotebook(file) {
    try {
        const notebook = JSON.parse(file.content);
        const cellsHTML = notebook.cells.map(cell => {
            if (cell.cell_type === 'markdown') {
                return `
                    <div class="notebook-cell markdown-cell">
                        <div class="cell-header">Markdown</div>
                        <div class="cell-content">${Array.isArray(cell.source) ? cell.source.join('') : cell.source}</div>
                    </div>
                `;
            } else if (cell.cell_type === 'code') {
                return `
                    <div class="notebook-cell code-cell">
                        <div class="cell-header">Code</div>
                        <div class="cell-content"><pre><code>${Array.isArray(cell.source) ? cell.source.join('') : cell.source}</code></pre></div>
                    </div>
                `;
            }
            return '';
        }).join('');

        return `
            <div class="file-preview">
                <h4><i class="fab fa-python"></i> ${file.name}</h4>
                <div class="notebook-container">
                    ${cellsHTML}
                </div>
            </div>
        `;
    } catch (error) {
        return renderGenericFile(file);
    }
}

// Render code file
function renderCodeFile(file) {
    const language = getLanguageFromExtension(file.name);
    return `
        <div class="file-preview">
            <h4><i class="fas fa-file-code"></i> ${file.name}</h4>
            <div class="code-container">
                <pre><code class="language-${language}">${escapeHtml(file.content)}</code></pre>
            </div>
        </div>
    `;
}

// Render generic file
function renderGenericFile(file) {
    return `
        <div class="file-preview">
            <h4><i class="fas fa-file"></i> ${file.name}</h4>
            <div class="file-info">
                <p>File size: ${formatFileSize(file.size || 0)}</p>
                <p>Type: ${file.type || 'Unknown'}</p>
            </div>
        </div>
    `;
}

// Helper functions
function getLanguageFromExtension(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const languages = {
        'py': 'python',
        'js': 'javascript',
        'html': 'html',
        'css': 'css',
        'md': 'markdown',
        'json': 'json'
    };
    return languages[ext] || 'text';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Close project modal
function closeProjectModal() {
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Download project
function downloadProject() {
    alert('Download functionality would be implemented here.');
}

// Share project
function shareProject() {
    if (navigator.share) {
        navigator.share({
            title: modalTitle.textContent,
            text: 'Check out this amazing project!',
            url: window.location.href
        });
    } else {
        // Fallback - copy to clipboard
        navigator.clipboard.writeText(window.location.href).then(() => {
            alert('Project URL copied to clipboard!');
        });
    }
}

// Add CSS for notebook cells
const notebookStyles = `
<style>
.notebook-container {
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    overflow: hidden;
    margin-top: 1rem;
}

.notebook-cell {
    border-bottom: 1px solid #e5e7eb;
}

.notebook-cell:last-child {
    border-bottom: none;
}

.cell-header {
    background: #f3f4f6;
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    font-weight: 600;
    color: #374151;
}

.cell-content {
    padding: 1rem;
}

.markdown-cell .cell-content {
    background: #f8fafc;
}

.code-cell .cell-content {
    background: #1f2937;
    color: #f9fafb;
}

.code-cell pre {
    margin: 0;
    font-family: 'Courier New', monospace;
    font-size: 0.875rem;
    line-height: 1.5;
}

.file-preview {
    margin-bottom: 2rem;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    overflow: hidden;
}

.file-preview h4 {
    background: #f3f4f6;
    margin: 0;
    padding: 1rem;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.code-container {
    background: #1f2937;
    color: #f9fafb;
    padding: 1rem;
    overflow-x: auto;
}

.code-container pre {
    margin: 0;
    font-family: 'Courier New', monospace;
    font-size: 0.875rem;
    line-height: 1.5;
}

.file-info {
    padding: 1rem;
    background: #f8fafc;
}

.project-details {
    background: white;
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
}
</style>
`;

// Inject notebook styles
document.head.insertAdjacentHTML('beforeend', notebookStyles);