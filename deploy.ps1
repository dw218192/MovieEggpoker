param (
    [Parameter(Mandatory = $false)]
    [int]$port = 8888,
    [switch]$dbg
)

if ($dbg) {
    Write-Host "Debug mode enabled"
    $env:FLASK_DEBUG = 1

    $webpack_job = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        npx webpack --watch
        Write-Host "Webpack job finished"
    }

    Start-Process powershell -PassThru -ArgumentList "-noexit -command (Invoke-Command -ScriptBlock {
        npx tailwindcss -i ./src/style.css -o ./movie_eggpoker/static/css/style_gen.css --watch
        Write-Host 'Tailwind job finished'
    })"

    # Set NODE_ENV for non-obfuscated webpack output
    $env:NODE_ENV = "debug"
}

try {
    $serve_job = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        if ($using:dbg) {
            hupper -m waitress --listen=localhost:$using:port --call movie_eggpoker:create_app
        } else {
            python -m waitress --listen=localhost:$using:port --call movie_eggpoker:create_app
        }
    }
    Write-Host "Spawned waitress job with ID " $serve_job.Id

    if ($dbg) {
        $jobs = @($webpack_job, $serve_job)
    }
    else {
        $jobs = @($serve_job)
    }

    while ($true) {
        $jobs | ForEach-Object {
            Receive-Job -Id $_.Id
        }
    }
}
finally {
    # Clean up jobs
    $jobs | ForEach-Object {
        Write-Host "Stopping job " $_.Id
        Stop-Job -Id $_.Id
        Remove-Job -Id $_.Id
    }
}
