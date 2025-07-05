from dataclasses import dataclass

@dataclass
class Movie:
    title: str
    movie: int
    url: str
    english_title: str = ""
    type: str = 'movie'
    
    def __hash__(self):
        return hash((self.movie, self.type, self.url))
    
    def __eq__(self, other):
        if not isinstance(other, Movie):
            return False
        return (self.movie, self.type, self.url) == (other.movie, other.type, other.url)