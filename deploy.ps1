param (
    [Parameter(Mandatory = $false)]
    [int]$port = 8888,
    [switch]$dbg
)

if ($dbg) {
    Write-Host "Debug mode enabled"
    $env:FLASK_DEBUG = 1

    $tailwind_job = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        npx tailwindcss -i ./src/style.css -o ./movie_eggpoker/static/css/style_gen.css --watch
        Write-Host "Tailwind job finished"
    }
    Write-Host "Spawned Tailwind job with ID " $tailwind_job.Id

    $webpack_job = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        npx webpack --watch
        Write-Host "Webpack job finished"
    }
    Write-Host "Spawned Webpack job with ID " $webpack_job.Id

    # Set NODE_ENV for non-obfuscated webpack output
    $env:NODE_ENV = "debug"
}


try {
    $serve_job = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        python.exe -m waitress --listen=localhost:$using:port --call movie_eggpoker:create_app
    }

    if ($dbg) {
        $jobs = @($tailwind_job, $webpack_job, $serve_job)
    }
    else {
        $jobs = @($serve_job)
    }

    Write-Host "Spawned waitress job with ID " $serve_job.Id

    while ($true) {
        $jobs | ForEach-Object {
            Receive-Job -Id $_.Id
        }
    }
}
finally {
    Write-Host "Cleaning up " $jobs.Count " jobs"

    $jobs | ForEach-Object {
        Write-Host "Stopping job " $_.Id
        Stop-Job -Id $_.Id
        Remove-Job -Id $_.Id
    }
}
