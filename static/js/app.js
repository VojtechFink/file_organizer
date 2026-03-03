// Global state
let currentDirectory = null;

// Set directory
async function setDirectory() {
    const path = document.getElementById('directoryPath').value;

    if (!path) {
        showMessage('Please enter a directory path', 'error');
        return;
    }

    try {
        const response = await fetch('/api/set-directory', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path: path })
        });

        const data = await response.json();

        if (response.ok) {
            currentDirectory = data.path;
            document.getElementById('currentPath').textContent = `Current directory: ${data.path}`;
            showMessage('Directory set successfully!', 'success');

            // Show sections and load stats
            document.getElementById('statsSection').classList.remove('hidden');
            document.getElementById('actionsSection').classList.remove('hidden');
            loadStatistics();
        } else {
            showMessage(data.detail || 'Error setting directory', 'error');
        }
    } catch (error) {
        showMessage('Error: ' + error.message, 'error');
    }
}

// Load statistics
async function loadStatistics() {
    try {
        const response = await fetch('/api/statistics');
        const stats = await response.json();

        // Update stats cards
        document.getElementById('totalFiles').textContent = stats.total_files;
        document.getElementById('totalSize').textContent = `${stats.total_size_mb.toFixed(2)} MB`;
        document.getElementById('fileTypes').textContent = Object.keys(stats.file_types).length;

        // File types chart
        renderFileTypesChart(stats.file_types);

        // Largest files
        renderLargestFiles(stats.largest_files);

        showMessage('Statistics loaded!', 'success');
    } catch (error) {
        showMessage('Error loading statistics: ' + error.message, 'error');
    }
}

// Render file types chart
function renderFileTypesChart(fileTypes) {
    const container = document.getElementById('fileTypesChart');
    container.innerHTML = '';

    const sortedTypes = Object.entries(fileTypes)
        .sort((a, b) => b[1].count - a[1].count)
        .slice(0, 10);

    const maxCount = sortedTypes[0]?.[1].count || 1;

    sortedTypes.forEach(([ext, data]) => {
        const percentage = (data.count / maxCount) * 100;
        const sizeMB = (data.size / (1024 * 1024)).toFixed(2);

        const bar = document.createElement('div');
        bar.className = 'flex items-center gap-4';
        bar.innerHTML = `
            <div class="w-24 text-sm font-medium text-gray-700">${ext}</div>
            <div class="flex-1 bg-gray-200 rounded-full h-6 relative">
                <div class="file-type-bar bg-gradient-to-r from-blue-500 to-blue-600 h-6 rounded-full flex items-center justify-end pr-2" 
                     style="width: ${percentage}%">
                    <span class="text-xs text-white font-semibold">${data.count}</span>
                </div>
            </div>
            <div class="w-20 text-sm text-gray-600">${sizeMB} MB</div>
        `;
        container.appendChild(bar);
    });
}

// Render largest files
function renderLargestFiles(files) {
    const container = document.getElementById('largestFiles');
    container.innerHTML = '';

    files.slice(0, 5).forEach(file => {
        const item = document.createElement('div');
        item.className = 'flex justify-between items-center p-3 bg-gray-50 rounded-lg';
        item.innerHTML = `
            <div class="flex-1 truncate">
                <p class="font-medium text-gray-800">${file.name}</p>
                <p class="text-xs text-gray-500 truncate">${file.path}</p>
            </div>
            <div class="text-right ml-4">
                <p class="font-semibold text-gray-800">${file.size_mb} MB</p>
            </div>
        `;
        container.appendChild(item);
    });
}

// Organize by type
async function organizeByType() {
    if (!confirm('Are you sure you want to organize files by type?')) return;

    try {
        const response = await fetch('/api/organize-by-type', {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok) {
            showMessage(data.message, 'success');
            loadStatistics();
        } else {
            showMessage(data.detail || 'Error organizing files', 'error');
        }
    } catch (error) {
        showMessage('Error: ' + error.message, 'error');
    }
}

// Organize by date
async function organizeByDate() {
    if (!confirm('Are you sure you want to organize files by date?')) return;

    try {
        const response = await fetch('/api/organize-by-date', {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok) {
            showMessage(data.message, 'success');
            loadStatistics();
        } else {
            showMessage(data.detail || 'Error organizing files', 'error');
        }
    } catch (error) {
        showMessage('Error: ' + error.message, 'error');
    }
}

// Find duplicates
async function findDuplicates() {
    try {
        showMessage('Searching for duplicates...', 'info');

        const response = await fetch('/api/find-duplicates');
        const data = await response.json();

        if (response.ok) {
            renderDuplicates(data.duplicates);
            document.getElementById('duplicatesSection').classList.remove('hidden');
            showMessage(`Found ${data.groups} groups of duplicates`, 'success');
        } else {
            showMessage(data.detail || 'Error finding duplicates', 'error');
        }
    } catch (error) {
        showMessage('Error: ' + error.message, 'error');
    }
}

// Render duplicates
function renderDuplicates(duplicates) {
    const container = document.getElementById('duplicatesList');
    container.innerHTML = '';

    if (duplicates.length === 0) {
        container.innerHTML = '<p class="text-gray-600">No duplicates found! 🎉</p>';
        return;
    }

    duplicates.forEach((group, index) => {
        const groupDiv = document.createElement('div');
        groupDiv.className = 'mb-4 p-4 bg-red-50 border border-red-200 rounded-lg';

        const wastedMB = (group.wasted_space / (1024 * 1024)).toFixed(2);

        groupDiv.innerHTML = `
            <h3 class="font-semibold text-gray-800 mb-2">
                Group ${index + 1} - ${group.count} files (Wasted: ${wastedMB} MB)
            </h3>
            <ul class="space-y-1">
                ${group.files.map(file => `<li class="text-sm text-gray-600 truncate">📄 ${file}</li>`).join('')}
            </ul>
        `;

        container.appendChild(groupDiv);
    });
}

// Remove duplicates
async function removeDuplicates() {
    if (!confirm('Are you sure you want to remove all duplicate files? This cannot be undone!')) return;

    try {
        const response = await fetch('/api/remove-duplicates', {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok) {
            showMessage(data.message, 'success');
            document.getElementById('duplicatesSection').classList.add('hidden');
            loadStatistics();
        } else {
            showMessage(data.detail || 'Error removing duplicates', 'error');
        }
    } catch (error) {
        showMessage('Error: ' + error.message, 'error');
    }
}

// Show message
function showMessage(message, type = 'info') {
    const messageBox = document.getElementById('messageBox');
    messageBox.classList.remove('hidden');

    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        info: 'bg-blue-500',
        warning: 'bg-yellow-500'
    };

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${colors[type]} text-white px-6 py-4 rounded-lg shadow-lg mb-2`;
    messageDiv.textContent = message;

    messageBox.appendChild(messageDiv);

    setTimeout(() => {
        messageDiv.remove();
        if (messageBox.children.length === 0) {
            messageBox.classList.add('hidden');
        }
    }, 3000);
}

// Enter key support for directory input
document.getElementById('directoryPath')?.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        setDirectory();
    }
});

// Analyze images
async function analyzeImages() {
    if (!confirm('This will analyze and organize all images by quality. Continue?')) return;

    try {
        showMessage('Analyzing images... This may take a while.', 'info');

        const response = await fetch('/api/analyze-images', {
            method: 'POST'
        });

        const data = await response.json();

        if (response.ok) {
            const msg = `
                Analysis complete!
                • Total: ${data.stats.total_analyzed}
                • Good: ${data.stats.good_images}
                • Blurry: ${data.stats.blurry_images}
                • Cropped: ${data.stats.cropped_faces}
                • Low-res: ${data.stats.low_resolution}
            `;
            showMessage(msg, 'success');
            loadStatistics();
        } else {
            showMessage(data.detail || 'Error analyzing images', 'error');
        }
    } catch (error) {
        showMessage('Error: ' + error.message, 'error');
    }
}

// Find similar images
async function findSimilarImages() {
    try {
        showMessage('Searching for similar images...', 'info');

        const response = await fetch('/api/find-similar-images');
        const data = await response.json();

        if (response.ok) {
            if (data.groups === 0) {
                showMessage('No similar images found! 🎉', 'success');
            } else {
                showMessage(`Found ${data.groups} groups of similar images`, 'success');
                renderSimilarImages(data.similar_images);
            }
        } else {
            showMessage(data.detail || 'Error finding similar images', 'error');
        }
    } catch (error) {
        showMessage('Error: ' + error.message, 'error');
    }
}

// Render similar images
function renderSimilarImages(groups) {
    const container = document.getElementById('duplicatesList');
    container.innerHTML = '<h3 class="text-xl font-bold mb-4">📸 Similar Images:</h3>';

    groups.forEach((group, index) => {
        const groupDiv = document.createElement('div');
        groupDiv.className = 'mb-4 p-4 bg-purple-50 border border-purple-200 rounded-lg';

        groupDiv.innerHTML = `
            <h4 class="font-semibold text-gray-800 mb-2">
                Group ${index + 1} - ${group.count} similar images
            </h4>
            <ul class="space-y-1">
                ${group.files.map(file => `
                    <li class="text-sm text-gray-600 truncate">🖼️ ${file}</li>
                `).join('')}
            </ul>
        `;

        container.appendChild(groupDiv);
    });

    document.getElementById('duplicatesSection').classList.remove('hidden');
}