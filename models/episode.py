from dataclasses import dataclass

@dataclass
class Episode:
    title: str
    season: int
    episode: int
    url: str
    type: str = 'episode'

    def __hash__(self):
        return hash((self.season, self.episode, self.type))
    
    def __eq__(self, other):
        if not isinstance(other, Episode):
            return False
        return (self.season, self.episode, self.type) == (other.season, other.episode, other.type)