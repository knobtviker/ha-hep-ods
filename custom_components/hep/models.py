"""Data models for HEP integration."""
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class HepAccount:
    """Class representing a HEP account (Kupac)."""
    korisnik_id: int
    dp: str
    sifra: str
    naziv: str
    adresa: str
    mjesto: str
    oib: str
    tarifni_model: str
    broj_brojila: str
    br_tarifa1: int
    br_tarifa2: int
    br_tarifa3: int
    datum_web_ocitanja: str
    ugovorni_racun: str
    pog_mjesto: str
    kupac_id: int

    @classmethod
    def from_dict(cls, data: dict) -> "HepAccount":
        """Create an instance from a dictionary."""
        return cls(
            korisnik_id=data.get("korisnikId"),
            dp=data.get("dp"),
            sifra=data.get("sifra"),
            naziv=data.get("naziv"),
            adresa=data.get("adresa"),
            mjesto=data.get("mjesto"),
            oib=data.get("oib"),
            tarifni_model=data.get("tarifniModel"),
            broj_brojila=data.get("brojBrojila"),
            br_tarifa1=data.get("brTarifa1", 0),
            br_tarifa2=data.get("brTarifa2", 0),
            br_tarifa3=data.get("brTarifa3", 0),
            datum_web_ocitanja=data.get("datumWebOcitanja"),
            ugovorni_racun=data.get("ugovorniRacun", "").strip(),
            pog_mjesto=data.get("pogMjesto"),
            kupac_id=data.get("kupacId"),
        )

@dataclass
class HepUser:
    """Class representing a HEP user."""
    email: str
    first_name: str
    last_name: str
    accounts: List[HepAccount]

    @classmethod
    def from_dict(cls, data: dict) -> "HepUser":
        """Create an instance from a dictionary."""
        accounts_data = data.get("kupci", [])
        accounts = [HepAccount.from_dict(acc) for acc in accounts_data]
        return cls(
            email=data.get("mail"),
            first_name=data.get("ime"),
            last_name=data.get("prezime"),
            accounts=accounts
        )

@dataclass
class HepPriceItem:
    """Price item (vt, nt, snaga)."""
    vt: float
    nt: float
    snaga: float

    @classmethod
    def from_dict(cls, data: dict) -> "HepPriceItem":
        return cls(
            vt=data.get("vt", 0.0),
            nt=data.get("nt", 0.0),
            snaga=data.get("snaga", 0.0),
        )

@dataclass
class HepTariffModel:
    """Tariff model (plavi, bijeli, crveni)."""
    proizvodnja: HepPriceItem
    prijenos: HepPriceItem
    distribucija: HepPriceItem
    mjerna_usluga: float

    @classmethod
    def from_dict(cls, data: dict) -> "HepTariffModel":
        return cls(
            proizvodnja=HepPriceItem.from_dict(data.get("proizvodnja", {})),
            prijenos=HepPriceItem.from_dict(data.get("prijenos", {})),
            distribucija=HepPriceItem.from_dict(data.get("distribucija", {})),
            mjerna_usluga=data.get("mjernaUsluga", 0.0),
        )

@dataclass
class HepPrices:
    """HEP Prices."""
    oie: float
    pdv: float
    opskrba: float
    plavi: HepTariffModel
    bijeli: HepTariffModel
    crveni: HepTariffModel

    @classmethod
    def from_dict(cls, data: dict) -> "HepPrices":
        return cls(
            oie=data.get("oie", 0.0),
            pdv=data.get("pdv", 0.0),
            opskrba=data.get("opskrba", 0.0),
            plavi=HepTariffModel.from_dict(data.get("plavi", {})),
            bijeli=HepTariffModel.from_dict(data.get("bijeli", {})),
            crveni=HepTariffModel.from_dict(data.get("crveni", {})),
        )

@dataclass
class HepBill:
    """Bill item (promet)."""
    kupac_id: int
    datum: str
    opis: str
    duguje: float
    potrazuje: float
    saldo: float
    dospijeva: str
    pnb: str
    iznos_ispis: float
    racun: str
    status: str

    @classmethod
    def from_dict(cls, data: dict) -> "HepBill":
        return cls(
            kupac_id=data.get("kupacId"),
            datum=data.get("datum"),
            opis=data.get("opis"),
            duguje=data.get("duguje", 0.0),
            potrazuje=data.get("potrazuje", 0.0),
            saldo=data.get("saldo", 0.0),
            dospijeva=data.get("dospijeva"),
            pnb=data.get("pnb"),
            iznos_ispis=data.get("iznosIspis", 0.0),
            racun=data.get("racun"),
            status=data.get("status"),
        )

@dataclass
class HepBalance:
    """Balance info (saldo)."""
    iznos: float
    opis: str
    iznos_val: str

    @classmethod
    def from_dict(cls, data: dict) -> "HepBalance":
        return cls(
            iznos=data.get("iznos", 0.0),
            opis=data.get("opis"),
            iznos_val=data.get("iznosVal"),
        )

@dataclass
class HepBillingInfo:
    """Billing info container."""
    bills: List[HepBill]
    balance: HepBalance

    @classmethod
    def from_dict(cls, data: dict) -> "HepBillingInfo":
        bills_data = data.get("promet", [])
        bills = [HepBill.from_dict(b) for b in bills_data]
        return cls(
            bills=bills,
            balance=HepBalance.from_dict(data.get("saldo", {}))
        )

@dataclass
class HepConsumption:
    """Consumption info (potrosnja)."""
    razdoblje: str
    tarifa1: int
    tarifa2: int
    tarifa3: int
    proizv1: int
    proizv2: int

    @classmethod
    def from_dict(cls, data: dict) -> "HepConsumption":
        return cls(
            razdoblje=data.get("razdoblje"),
            tarifa1=data.get("tarifa1", 0),
            tarifa2=data.get("tarifa2", 0),
            tarifa3=data.get("tarifa3", 0),
            proizv1=data.get("proizv1", 0),
            proizv2=data.get("proizv2", 0),
        )

@dataclass
class HepWarning:
    """Warning/Notification info (opomena)."""
    datum_izdavanja: str
    broj_dokumenta: Optional[str]
    razina: str
    stanje: float

    @classmethod
    def from_dict(cls, data: dict) -> "HepWarning":
        return cls(
            datum_izdavanja=data.get("datumIzdavanja"),
            broj_dokumenta=data.get("brojDokumenta"),
            razina=data.get("razina"),
            stanje=float(data.get("stanje", 0.0)),
        )

@dataclass
class HepOmmCheckStatus:
    """Status of OMM check."""
    status: int
    opis: str

    @classmethod
    def from_dict(cls, data: dict) -> "HepOmmCheckStatus":
        return cls(
            status=data.get("Status", 0),
            opis=data.get("Opis", ""),
        )

@dataclass
class HepOmmCheck:
    """OMM Check result (Provjera_OmmDto)."""
    br_tarifa: int
    omm: str
    br_tarifa_1: int
    tarifa1_od: int
    tarifa1_do: int
    br_tarifa_2: int
    tarifa2_od: int
    tarifa2_do: int
    status: HepOmmCheckStatus

    @classmethod
    def from_dict(cls, data: dict) -> "HepOmmCheck":
        return cls(
            br_tarifa=data.get("Br_Tarifa", 0),
            omm=data.get("Omm", ""),
            br_tarifa_1=data.get("Br_Tarifa_1", 0),
            tarifa1_od=data.get("Tarifa1_Od", 0),
            tarifa1_do=data.get("Tarifa1_Do", 0),
            br_tarifa_2=data.get("Br_Tarifa_2", 0),
            tarifa2_od=data.get("Tarifa2_Od", 0),
            tarifa2_do=data.get("Tarifa2_Do", 0),
            status=HepOmmCheckStatus.from_dict(data.get("Status", {})),
        )

@dataclass
class HepReadingSubmissionResult:
    """Result of reading submission (Dostava)."""
    status: int
    posalji: int
    opis: str

    @classmethod
    def from_dict(cls, data: dict) -> "HepReadingSubmissionResult":
        return cls(
            status=data.get("Status", 0),
            posalji=data.get("Posalji", 0),
            opis=data.get("Opis", ""),
        )
