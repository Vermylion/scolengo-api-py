# Skolengo's API
Skolengo's API is not available to anyone, only schools that use their service. However, this library has to work somehow, and uses Skolengo's API. So, here is documented links to use their API, if you want to translate it into another language for example (I struggled without it :) ).

## Base URL
The Skolengo API comes from the same base url. All following links are prefixed by this link.

**Base URL:** `https://api.skolengo.com/api/v1/bff-sko-app`

## Authentification

To authenticate yourself and have access to the API, you need to retrieve an access token. The token is an openid-connect token.

Here are base 64 encoded oid client id and secret for the token:

**OID_CLIENT_ID:** `U2tvQXBwLlByb2QuMGQzNDkyMTctOWE0ZS00MWVjLTlhZjktZGY5ZTY5ZTA5NDk0`

**OID_CLIENT_SECRET:** `N2NiNGQ5YTgtMjU4MC00MDQxLTlhZTgtZDU4MDM4NjkxODNm` 

### School
To get access to the access token, you first have to retrieve necessary school info from Skolengo.
The link that allows you to do so is this:
`/schools` (prefixed by the base url). This request to the API needs some parameters as well: 

`page[limit]`: The maximumn number of schools the api returns.

`page[offset]`: Is 0 by default (don't know what it does).

`filter[text]`: This is the name/input of the school you wish to access the information of.

### Token
Once you've generated an authorization link using various openid-connect libraries, the access url to the token will start with this:

**REDIRECT_URI**: `skoapp-prod://sign-in-callback`

## Used links

`/sko-app-configs/current`

`/schools`

`/users-info/{user id}`

`/schools-info`

`/schools-info/{school id}`

`/evaluations-settings`

`/evaluation-services`

`/evaluations/{evaluation id}`

`/periodic-reports-files`

`/agendas`

`/lessons/{lesson id}`

`/homework-assignments`

`/homework-assignments/{homework id}`

`/users-mail-settings/{user id}`

`/communications`

`/communications/{communication id}`

`/communications/{communication id}/participants`

`/communications/{communication id}/participations`

`/communications/{communication id}/relationships/folders`

`/participations`

`/absence-files`

`/absence-files/{folder id}`

`/absence-files-states`

`/absence-reasons`