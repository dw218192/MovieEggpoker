# check if env already exists
conda list -n flask_env
if ($lastexitcode -eq 0) {
    Write-Output "Environment already exists"
} else {
    Write-Output "Creating environment"
    conda create -n flask_env python=3.10 pip
}

if ($lastexitcode -eq 0) {
    Write-Output "Environment created"
} else {
    Write-Output "Failed to create environment"
    Exit
}

conda activate flask_env
conda install flask opencv requests
pip install yt-dlp gunicorn waitress youtube-search-python
pip install hupper # for waitress auto-reload
npm install webpack webpack-cli
npm install -D tailwindcss
npx tailwindcss init