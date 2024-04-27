param (
    [Parameter(Mandatory=$false)]
    [int]$port = 8888,
    [switch]$dbg
)

if ($dbg) {
    Write-Host "Debug mode enabled"
    $env:FLASK_DEBUG = 1
    $process = Start-Job -ScriptBlock {
        npx tailwindcss -i ./src/style.css -o ./movie_eggpoker/static/css/style_gen.css --watch
    }
    Write-Host "Spawned job " $process.Id
}

try {
    # Start the Flask server using Waitress
    Start-Process -NoNewWindow -Wait -FilePath "python" -ArgumentList "-m waitress --listen=localhost:$port --call movie_eggpoker:create_app"
} finally {
    Write-Host "Cleaning up..."
    if ($dbg -and $process) {
        Stop-Job -Id $process.Id -Force
        Remove-Job -Id $process.Id -Force
    }
}
