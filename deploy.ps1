param (
    [Parameter(Mandatory=$false)]
    [int]$port = 6666
)

waitress-serve --listen=0.0.0.0:$port --call movie_eggpoker:create_app