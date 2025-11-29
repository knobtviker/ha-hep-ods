"""Mock HEP API Server."""
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Dummy database
USERS = {
    "testuser": "password123",
    "bojan.komljenovic@gmail.com": "uWKrB.J62nN2zP3Xh8qd@B6KtYDkw7TH"
}

@app.route('/elektra/v1/api/korisnik/prijava', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username in USERS and USERS[username] == password:
        # Return the mock response structure provided by the user
        return jsonify({
            "mail": username,
            "status": None,
            "ime": "Test",
            "prezime": "User",
            "pwd": None,
            "activCode": None,
            "lastLogin": datetime.now().isoformat(),
            "lastAddress": None,
            "korisnikId": 90271143,
            "prvaPrijava": None,
            "kupci": [
                {
                    "korisnikId": 90271143,
                    "dp": "4001",
                    "sifra": "36347250",
                    "naziv": "TEST USER",
                    "adresa": "TEST ADDRESS 1, 10000 ZAGREB, HR",
                    "mjesto": "",
                    "oib": "12345678901",
                    "tarifniModel": "kućanstvo bijeli",
                    "brojBrojila": "0126535651",
                    "brCijela": 0,
                    "brDecimale": 0,
                    "brBrTarifa": 2,
                    "brTarifa1": 25015,
                    "brTarifa1Od": 25015,
                    "brTarifa1Do": 25027,
                    "brTarifa2": 11328,
                    "brTarifa2Od": 11328,
                    "brTarifa2Do": 11333,
                    "brTarifa3": 0,
                    "brTarifa3Od": 0,
                    "brTarifa3Do": 0,
                    "brVrijemeOcitanja": datetime.now().isoformat(),
                    "brDatumOcitanjaOd": datetime.now().isoformat(),
                    "brDatumOcitanjaDo": datetime.now().isoformat(),
                    "datumWebOcitanja": datetime.now().isoformat(),
                    "brObracunato": "",
                    "datumUnosa": datetime.now().isoformat(),
                    "kupacId": 80394346,
                    "master": "Y",
                    "pogNaziv": "HEP ELEKTRA D.O.O.",
                    "pogAdresa": "ULICA GRADA VUKOVARA 37",
                    "pogZiro": "HR9223400091510077598",
                    "datumIducegObracuna": "28.02.2026",
                    "rn2Mail": "0",
                    "rn2MailValue": "",
                    "ugovorniRacun": "2200757339  ",
                    "pogMjesto": "ZAGREB",
                    "mailPodsjetnik": "0",
                    "poslovniPartner": "1000225435"
                }
            ],
            "token": None
        }), 200
    
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/elektra/v1/api/obracun/cjenik', methods=['GET'])
def get_prices():
    # Return dummy pricing data matching the user's provided structure
    return jsonify({
        "oie": 0.013239,
        "pdv": 0.13,
        "opskrba": 0.982,
        "plavi": {
            "proizvodnja": {
                "vt": 0.091324,
                "nt": 0,
                "snaga": 0
            },
            "prijenos": {
                "vt": 0.013378,
                "nt": 0,
                "snaga": 0
            },
            "distribucija": {
                "vt": 0.032703,
                "nt": 0,
                "snaga": 0
            },
            "mjernaUsluga": 1.724
        },
        "bijeli": {
            "proizvodnja": {
                "vt": 0.097189,
                "nt": 0.047688,
                "snaga": 0
            },
            "prijenos": {
                "vt": 0.019324,
                "nt": 0.007432,
                "snaga": 0
            },
            "distribucija": {
                "vt": 0.038649,
                "nt": 0.017838,
                "snaga": 0
            },
            "mjernaUsluga": 1.724
        },
        "crveni": {
            "proizvodnja": {
                "vt": 0.097189,
                "nt": 0.047688,
                "snaga": 0
            },
            "prijenos": {
                "vt": 0.007432,
                "nt": 0.002972,
                "snaga": 2.155
            },
            "distribucija": {
                "vt": 0.02527,
                "nt": 0.011892,
                "snaga": 3.642
            },
            "mjernaUsluga": 6.139
        }
    }), 200

@app.route('/elektra/v1/api/promet/<int:kupac_id>', methods=['GET'])
def get_billing(kupac_id):
    # Return dummy billing data
    return jsonify({
    "promet": [
        {
            "kupacId": 80394346,
            "datum": "2025-12-05T00:00:00",
            "opis": "Akontacija",
            "duguje": 17.69,
            "potrazuje": 0,
            "saldo": 0,
            "dospijeva": "2025-12-05T00:00:00",
            "pnb": "2200757339-251103-2",
            "iznosIspis": 17.69,
            "racun": "",
            "status": "GREEN"
        },
        {
            "kupacId": 80394346,
            "datum": "2025-11-05T00:00:00",
            "opis": "Akontacija",
            "duguje": 17.53,
            "potrazuje": 0,
            "saldo": 0,
            "dospijeva": "2025-11-05T00:00:00",
            "pnb": "2200757339-251002-8",
            "iznosIspis": 17.53,
            "racun": "",
            "status": "GREEN"
        }
    ],
    "saldo": {
        "iznos": 39.92,
        "opis": "Preplata na dan 29.11.2025:",
        "iznosVal": "EUR"
    }
}), 200

@app.route('/elektra/v1/api/potrosnja/<int:kupac_id>', methods=['GET'])
def get_consumption(kupac_id):
    # Return dummy consumption data
    return jsonify([
        {
            "razdoblje": "30.08.2025 - 31.08.2025",
            "tarifa1": 12,
            "tarifa2": 5,
            "tarifa3": 0,
            "proizv1": 0,
            "proizv2": 0
        },
        {
            "razdoblje": "01.04.2025 - 29.08.2025",
            "tarifa1": 1535,
            "tarifa2": 676,
            "tarifa3": 0,
            "proizv1": 0,
            "proizv2": 0
        }
    ]), 200

@app.route('/elektra/v1/api/opomene/<int:kupac_id>', methods=['GET'])
def get_warnings(kupac_id):
    # Return dummy warnings data
    return jsonify([
        {
            "datumIzdavanja": "2025-06-26T00:00:00Z",
            "brojDokumenta": None,
            "razina": "Opomena pred obustavu isporuke i utuženje",
            "stanje": "36.44"
        },
        {
            "datumIzdavanja": "2022-07-31T00:00:00Z",
            "brojDokumenta": None,
            "razina": "Opomena pred obustavu isporuke i utuženje",
            "stanje": "475.54"
        }
    ]), 200

@app.route('/Omm/Provjera_Omm', methods=['POST'])
def check_omm():
    # Return dummy OMM check data
    return jsonify({
        "Provjera_OmmDto": {
            "Br_Tarifa": 2,
            "Omm": "0126535651",
            "Br_Tarifa_1": 0,
            "Tarifa1_Od": 0,
            "Tarifa1_Do": 0,
            "Br_Tarifa_2": 0,
            "Tarifa2_Od": 0,
            "Tarifa2_Do": 0,
            "Status": {
                "Status": 1,
                "Opis": "ok"
            }
        },
        "encValue": "irALbuKeATFsswqSNz6zAry97VNH+Fgp1Uge9Q6DY8NVqj/8bvc88hONUwwM5DqNbHQRYOXfi9//ddHNpy9V+YzudCLQK1TCfSsIFPW2eohZjis8ZH1+qFET5cEZqH51ntphDRJ41299mx9nqM72nLRnzyiVEzSxeM9AvywnR2kjvbCAw4sLMrwGxwJu4MAW9EkHUFteRr6Zb+onCiMUEHnW/LQptfGP0ddTXmHQZkA="
    }), 200

@app.route('/Omm/Dostava', methods=['POST'])
def submit_reading():
    # Return dummy submission result
    # We can simulate the two-step process based on Posalji param
    data = request.form
    posalji = data.get('DostavaVM.Posalji')
    
    if posalji == '0':
        return jsonify({
            "Status": 0,
            "Posalji": 1,
            "Opis": "Unesene vrijednosti odstupaju od očekivanog raspona potrošnje."
        }), 200
    else:
        return jsonify({
            "Status": 1,
            "Opis": "ok"
        }), 200

if __name__ == '__main__':
    app.run(port=5001, debug=True)
