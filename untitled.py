import musicbrainzngs
import time

musicbrainzngs.set_useragent(
    "musicbrainz-data-analysis", "0.1", "https://github.com/vitorbatalha"
)
musicbrainzngs.set_rate_limit(40)

def get_album_info(nome_album, nome_artista=None):
    try:
        # Procurando release groups pelo titulo do album e opcionalmente pelo artista.
        # O limite é 1 para pegar o primeiro resultado.
        res = musicbrainzngs.search_release_groups(
            releasegroup=nome_album,
            artist=nome_artista if nome_artista else None,
            limit=1
        )
        if not res["release-group-list"]:
            return {"album": nome_album, "Erro": "Não encontrado"}

        rg = res["release-group-list"][0]
        rgid = rg["id"]

        # Step 2: Fetch details with includes
        details = musicbrainzngs.get_release_group_by_id(
            rgid,
            includes=["releases", "tags"]
        )

        release_group = details["release-group"]

        # Choose the first release for track info
        release_id = release_group["release-list"][0]["id"]
        release = musicbrainzngs.get_release_by_id(
            release_id,
            includes=["recordings", "release-groups"]
        )["release"]

        # Step 3: Extract track info
        tracks = []
        total_length = 0
        for medium in release.get("medium-list", []):
            for track in medium.get("track-list", []):
                title = track["recording"]["title"]
                length_ms = int(track["recording"].get("length", 0))
                total_length += length_ms
                tracks.append({
                    "title": title,
                    "length_sec": round(length_ms / 1000, 2)
                })

        # Step 4: Extract metadata
        country = release.get("country", "unknown")
        genres = [tag["name"] for tag in release_group.get("tag-list", [])]

        return {
            "album": release["title"],
            "artist": release["artist-credit"][0]["artist"]["name"],
            "country": country,
            "track_count": len(tracks),
            "total_length_min": round(total_length / 60000, 2),
            "genres": genres,
            "tracks": tracks
        }

    except musicbrainzngs.WebServiceError as e:
        return {"album": nome_album, "error": str(e)}


    return None