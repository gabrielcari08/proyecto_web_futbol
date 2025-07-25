# ---- Titulares App ----

## Objtivo del proyecto:

> Crear una plataforma web en la que los usuarios puedan armar su equipo ideal con jugadores reales de la Primera División del fútbol argentino. Luego de cada fecha, se cargan los rendimientos de los jugadores reales y se calculan los puntos que cada usuario obtiene según el rendimiento de su equipo.

## Tecnologías usadas (hasta el momento)

- Backend: Python 3.11, FastAPI
- Base de datos: PostgreSQL 16 (vía Docker)
- ORM: SQLAlchemy
- Validaciones: Pydantic / pydantic-settings
- Entorno de trabajo: Docker + entorno virtual local
- Herramientas: DBeaver, VSCode, GitHub
- Documentación automática: Swagger (FastAPI)

## Configuración del entorno

### Estructura de ramas en git:

- main: rama principal del proyecto.
- dev: rama de desarrollo principal.
- db-setup: rama dedicada a la producción y configuración de la base de datos.
- fastapi-setup: rama que se dedica a la estructura para levantar fastapi
- user-setup: rama en donde construi el registro y autenticacion de usuarios
- team-setup: rama que sirve para el armado de equipos por el usuario.
- point-system: rama que se encarga de la logica de puntos.
- ranking-setup: rama que muestra los rankings regional y general de usuarios.

### Docker

- Archivo ***docker-compose.yaml***

```
version: '3.9'

services:
  db:
    image: postgres:16
    restart: always
    env_file:
      - .env
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

- Archivo ***.env***

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=titulares_db
```

## Base de Datos

### Conexión a la Base de Datos (archivo ***database.py***)

```
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

DATABASE_URL = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base() #<- Necesario para que los modelos funcionen. 
```

### Configuracion por entorno (archivo ***config.py***)

### Creación de Tablas (archivo ***create_tables.py***)

```
from app.models.user import User
from app.models.player import Player
from app.models.date import TournamentDate
from app.models.user_team import UserTeam
from app.models.performance import PlayerPerformance
from app.models.ranking import RegionalRanking
from app.models.team_player import UserTeamPlayer
from app.database import engine, Base

# Registrar modelos
Base.metadata.create_all(bind=engine)
```

### Modelos creados hasta el momento

> Los modelos representan las entidades principales del sistema, incluyendo relaciones por claves foráneas.

| Entidad              | Descripción                                                               |
| -------------------- | ------------------------------------------------------------------------- |
| `Usuario`            | Usuario del sistema (nombre, contraseña hasheada, región, fecha ingreso)  |
| `Jugador`            | Jugadores reales (nombre, club, posición, valor, edad, si es sub23)       |
| `FechaTorneo`        | Fechas del torneo (inicio, fin, si está cerrada)                          |
| `EquipoUsuario`      | Un equipo creado por el usuario en una fecha específica                   |
| `EquipoJugador`      | Relación entre los jugadores elegidos para el equipo del usuario          |
| `RendimientoJugador` | Estadísticas de cada jugador por fecha (goles, asistencias, puntos, etc.) |
| `RankingRegional`    | Tabla con el puntaje total de un usuario en su región                     |

> Un Usuario puede tener un solo EquipoUsuario por FechaTorneo

### Relaciones entre las tablas

> La base de datos está diseñada para reflejar la lógica del juego de fantasy basado en fútbol argentino. A continuación, se detalla cómo se relacionan las tablas entre sí:

#### Usuario (users)
> Un usuario puede crear un equipo por cada fecha del torneo.

##### Se relaciona con:

- UserTeam (Equipo del usuario en una fecha)
- RegionalRanking (ranking del usuario según su región)

#### Player (players)
> Representa a los jugadores reales del torneo.

##### Se relaciona con:

- TeamPlayer (cuando es seleccionado por un usuario en un equipo)
- PlayerPerformance (cuando juega una fecha y se registran sus estadísticas)
- UserTeam (cuando es elegido como capitán)

#### TournamentDate (matchdays)
> Define cada jornada o fecha del torneo.

##### Se relaciona con:

- UserTeam (un equipo por usuario en cada fecha)
- PlayerPerformance (estadísticas individuales de cada jugador en esa fecha)
- RegionalRanking (ranking acumulado de usuarios en esa fecha)

#### UserTeam (user_teams)
> Es el equipo que un usuario arma para una fecha específica.

##### Se relaciona con:

- Usuario (quién creó el equipo)
- TournamentDate (fecha para la que fue creado)
- TeamPlayer (jugadores que componen el equipo)
- Player (jugador que fue elegido como capitán)

> Restricción: Un usuario puede tener solamente un UserTeam por cada TournamentDate.

#### TeamPlayer (team_player)

- Es una tabla intermedia que une jugadores (Player) con equipos (UserTeam).
- Representa qué jugadores forman parte de un equipo en una fecha determinada.
- Cada fila representa un jugador incluido en un equipo, junto con su rol (titular o suplente, aunque ahora todos serán considerados como parte del plantel sin suplentes).

> Esta tabla intermedia permite manejar relaciones de muchos a muchos entre jugadores y equipos:
- Un jugador puede estar en muchos equipos (por ejemplo, si muchos usuarios lo eligen), y un equipo tiene muchos jugadores.

#### PlayerPerformance (performances)
> Registra el rendimiento de un jugador real en una fecha específica.

##### Se relaciona con:

- Player (jugador evaluado)
- TournamentDate (fecha donde se evaluó)

##### Incluye campos como goles, asistencias, tarjetas, MVP, etc., y los puntos obtenidos.

#### RegionalRanking (regional_rankings)
> Representa el puntaje acumulado de un usuario en su región para una fecha específica.

##### Se relaciona con:

- Usuario
- TournamentDate

> Puede servir para mostrar los mejores equipos por provincia o región.