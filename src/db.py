from functools import cache
import json
import math

from types import SimpleNamespace
from typing import Any, Type, TypeVar, Generic, Callable

from loader import load_files

T = TypeVar("T")

Js = dict[str, Any]


def to_data(data: str | Js) -> Js:
    return data if isinstance(data, dict) else json.loads(data)


def f(x: Any) -> float:
    return float(x)


class DB:
    """
    Namespace
    """

    properties: "Database[Property]"
    manufacturers: "Database[Manufacturer]"
    engines: "Database[Engine]"
    aircraft_types: "Database[AircraftType]"
    aircraft_models: "Database[AircraftModel]"


class Database(Generic[T]):
    """
    Must have id
    """

    def __init__(self, loader: Callable[[Js], T], data: list[Js] = []):
        if isinstance(data, str):
            data = json.loads(data)
            # should be a list
            assert isinstance(data, list)

        self.dict = {str(item["id"]): loader(item) for item in data}

    def __getitem__(self, key: str) -> T:
        return self.dict[key]

    def __setitem__(self, key: str, value: T) -> None:
        self.dict[key] = value

    def __delitem__(self, key: str) -> None:
        del self.dict[key]

    def __contains__(self, key: str) -> bool:
        return key in self.dict


class ILoadable:
    def __init__(self):
        self.id: str

    @staticmethod
    def from_data(data: Js) -> "ILoadable":
        raise NotImplementedError


class Property(ILoadable):
    @staticmethod
    def from_data(data: Js) -> "Property":
        return Property(data["id"], data["name"], data["type"], data.get("unit"))

    def __init__(self, id: str, name: str, type: str, unit: str | None = None):
        self.id = id
        self.name = name
        self.type = type
        self.unit = unit

    def __repr__(self):
        return f"{self.name} ({self.type})"


class PropertyValue(ILoadable):
    @staticmethod
    def from_data(data: Js) -> "PropertyValue":
        return PropertyValue(data["property"], data["value"])

    def __init__(self, property: str, value: Js):
        self.id = property
        self.property = DB.properties[property]
        self.value = value

    @property
    def name(self) -> str:
        return self.property.name

    def __repr__(self):
        return f"{self.property.name}: {self.value}"


ELT = TypeVar("ELT", bound=ILoadable)


class EntryList(dict[str, ELT], Generic[ELT]):
    @staticmethod
    def from_data(Entry: Type[ELT], data: list[Js]) -> "EntryList[ELT]":
        return EntryList[ELT]([Entry.from_data(item) for item in data])

    def __init__(self, data: list[ELT] = []):
        super().__init__({item.id: item for item in data})

    def by(self, property: str, value: Any):
        for item in self.values():
            if getattr(item, property) == value:
                return item

    def first(self) -> ELT | None:
        if len(self) == 0:
            return None
        return next(iter(self.values()))

    @property
    def list(self) -> list[ELT]:
        return list(self.values())


class Manufacturer(ILoadable):
    @staticmethod
    def from_data(data: Js) -> "Manufacturer":
        return Manufacturer(
            data["id"],
            data["country"],
            data["name"],
            data["nativeName"],
            [PropertyValue.from_data(d) for d in data["propertyValues"]],
            data["tags"],
            data["url"],
        )

    def __init__(
        self,
        id: str,
        country: str,
        name: str,
        native_name: str | None,
        property_values: list[PropertyValue],
        tags: list[str],
        url: str,
    ):
        self.id = id
        self.country = country
        self.name = name
        self.native_name = native_name
        self.property_values = EntryList(property_values)
        self.tags = tags
        self.url = url


class Engine(ILoadable):
    @staticmethod
    def from_data(data: Js) -> "Engine":
        return Engine(
            data["id"],
            data["name"],
            data["nativeName"],
            data["engineFamily"],
            [PropertyValue.from_data(d) for d in data["propertyValues"]],
            data["tags"],
            data["url"],
        )

    def __init__(
        self,
        id: str,
        name: str,
        native_name: str | None,
        engine_family: str,
        property_values: list[PropertyValue],
        tags: list[str],
        url: str,
    ):
        self.id = id
        self.name = name
        self.native_name = native_name
        self.engine_family = engine_family
        self.property_values = EntryList(property_values)
        self.tags = tags
        self.url = url


class JetInformation(SimpleNamespace):
    def __init__(
        self,
        inlet_area: float,
        exit_area: float,
        inlet_pressure: float,
        exit_pressure: float,
        compresser_ratio: float,
        inlet_temperature: float,
        diffuser_pressure_increase: float,
        weight: float,
    ):
        self.inlet_area = inlet_area
        self.exit_area = exit_area
        self.inlet_pressure = inlet_pressure
        self.exit_pressure = exit_pressure
        self.compresser_ratio = compresser_ratio
        self.inlet_temperature = inlet_temperature
        self.diffuser_pressure_increase = diffuser_pressure_increase
        self.weight = weight


class AircraftType(ILoadable):
    @staticmethod
    def from_data(data: Js) -> "AircraftType":
        return AircraftType(
            data["id"],
            data["aircraftFamily"],
            data["engineCount"],
            data["engineFamily"],
            [DB.engines[id] for id in data["engineModels"]],
            data["iataCode"],
            data["icaoCode"],
            DB.manufacturers[data["manufacturer"]],
            data["name"],
            data["nativeName"],
            [PropertyValue.from_data(d) for d in data["propertyValues"]],
            data["tags"],
            data["url"],
        )

    def __init__(
        self,
        id: str,
        aircraft_family: str,
        engine_count: int,
        engine_family: str,
        engine_models: list[Engine],
        iata_code: str | None,
        icao_code: str | None,
        manufacturer: Manufacturer,
        name: str,
        native_name: str | None,
        property_values: list[PropertyValue],
        tags: list[str],
        url: str,
    ):
        self.id = id
        self.aircraft_family = aircraft_family
        self.engine_count = engine_count
        self.engine_family = engine_family
        self.engine_models = EntryList(engine_models)
        self.iata_code = iata_code
        self.icao_code = icao_code
        self.manufacturer = manufacturer
        self.name = name
        self.native_name = native_name
        self.property_values = EntryList(property_values)
        self.tags = tags
        self.url = url

    @staticmethod
    @cache
    def get_engine_properties():
        return SimpleNamespace(
            fan_diameter="1ec851ba-80a1-6f2c-b99a-73b681400edf",
            # exit_area="exitArea",
            # inlet_pressure="",
            # exit_pressure="exitPressure",
            compresser_ratio="1ec851b8-7423-66e4-b99a-b9dd6344f5b6",
            # inlet_temperature="inletTemperature",
            # diffuser_pressure_increase="diffuserPressureIncrease",
            weight="1ec851b9-dc27-6438-b99a-c98b7ffb3c70",
        )

    @property
    @cache
    def jet_information(self) -> JetInformation | None:
        try:
            p = self.get_engine_properties()
            first = self.engine_models.first()
            if first is None:
                return
            pv = first.property_values

            inlet_area = (f(pv[p.fan_diameter].value) / 2) ** 2 * math.pi

            # This ration is not perfect, but it's close enough
            exit_area = inlet_area * 0.6

            # 50kPa, around 4km altitude
            inlet_pressure = 50_000

            exit_pressure = inlet_pressure

            compresser_ratio = f(pv[p.compresser_ratio].value)

            # Arbitrary values taken from book
            inlet_temperature = 1120
            diffuser_pressure_increase = 30_000

            weight = f(pv[p.weight].value)

            return JetInformation(
                inlet_area,
                exit_area,
                inlet_pressure,
                exit_pressure,
                compresser_ratio,
                inlet_temperature,
                diffuser_pressure_increase,
                weight,
            )
        except KeyError:
            return


class AircraftModel(ILoadable):
    @staticmethod
    def from_data(data: Js) -> "AircraftModel":
        return AircraftModel(
            data["id"],
            data["aircraftType"],
            data["url"],
        )

    def __init__(
        self,
        id: str,
        aircraft_type: str,
        url: str,
    ):
        self.id = id
        self.aircraft_type = aircraft_type
        self.url = url


def load(path: str) -> Type[DB]:
    data: dict[str, list[Js]] = load_files(path)  # type: ignore

    DB.properties = Database[Property](Property.from_data, data["properties"])
    DB.engines = Database[Engine](Engine.from_data, data["engine_models"])
    DB.manufacturers = Database[Manufacturer](
        Manufacturer.from_data, data["manufacturers"]
    )
    DB.aircraft_types = Database[AircraftType](
        AircraftType.from_data, data["aircraft_types"]
    )
    DB.aircraft_models = Database[AircraftModel](
        AircraftModel.from_data, data["aircraft_models"]
    )

    # fixup

    an2 = "1ed012dc-450c-6c9c-9ea9-e93d5bae89a8"

    for key, value in list(DB.aircraft_types.dict.items()):
        if key == an2:
            del DB.aircraft_types.dict[key]

    for key, value in list(DB.aircraft_models.dict.items()):
        if value.aircraft_type == an2:
            del DB.aircraft_models.dict[key]

    return DB


__all__ = ["load"]
