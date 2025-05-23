from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import hashlib
import time
import requests
import threading

### ==== LOGIQUE DE BLOCKCHAIN ==== ###

# Fonction pour hasher une chaîne de caractères avec SHA-256
def sha256(data):
    return hashlib.sha256(data.encode()).hexdigest()

# Fonction pour générer une racine de Merkle à partir de hash de transactions
def merkle_root(hashes):
    if not hashes:
        return None
    while len(hashes) > 1:
        if len(hashes) % 2 != 0:
            hashes.append(hashes[-1])  # Si nombre impair, on duplique le dernier
        hashes = [sha256(hashes[i] + hashes[i+1]) for i in range(0, len(hashes), 2)]
    return hashes[0]

# Classe représentant un bloc dans la blockchain
class Block:
    def __init__(self, index, transactions, previous_hash, difficulty=2):
        self.index = index  # Position du bloc
        self.timestamp = time.time()  # Timestamp de création
        self.transactions = transactions  # Liste des transactions
        self.previous_hash = previous_hash  # Hash du bloc précédent
        self.difficulty = difficulty  # Difficulté du minag e
        self.nonce = 0  # Compteur pour le minage
        self.merkle_root = merkle_root([sha256(tx) for tx in transactions])  # Merkle Root
        self.hash = self.compute_hash()  # Hash initial

    # Méthode qui génère le hash du bloc
    def compute_hash(self):
        block_string = f"{self.index}{self.timestamp}{self.transactions}{self.previous_hash}{self.nonce}{self.merkle_root}"
        return sha256(block_string)

    # Méthode de minage : recherche un hash commençant par N zéros
    def mine(self):
        target = '0' * self.difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.compute_hash()
        print(f"✅ Bloc {self.index} miné : {self.hash[:10]}...")

    # Transforme un bloc en dictionnaire pour JSON
    def to_dict(self):
        return self.__dict__

# Classe représentant la blockchain elle-même
class Blockchain:
    def __init__(self, difficulty=2):
        self.chain = []  # La chaîne de blocs
        self.difficulty = difficulty
        self.create_genesis_block()  # Création du bloc initial

    # Création du bloc "Genesis"
    def create_genesis_block(self):
        self.chain.append(Block(0, ["Genesis Block"], "0", self.difficulty))

    # Ajout d'un nouveau bloc à partir des transactions
    def add_block(self, transactions):
        last_block = self.chain[-1]
        new_block = Block(len(self.chain), transactions, last_block.hash, self.difficulty)
        new_block.mine()
        self.chain.append(new_block)

    # Validation de la chaîne (preuve de travail, hash, liens, merkle)
    def is_valid(self):
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]
            if curr.hash != curr.compute_hash():
                return False
            if curr.previous_hash != prev.hash:
                return False
            if not curr.hash.startswith('0' * self.difficulty):
                return False
            expected_merkle = merkle_root([sha256(tx) for tx in curr.transactions])
            if curr.merkle_root != expected_merkle:
                return False
        return True

    # Remplace la chaîne actuelle par une autre si elle est plus longue ET valide
    def replace_chain(self, new_chain):
        if len(new_chain) > len(self.chain) and self.validate_external_chain(new_chain):
            self.chain = [self.dict_to_block(b) for b in new_chain]

    # Vérifie qu'une chaîne reçue est valide (hash, timestamps, etc.)
    def validate_external_chain(self, chain_data):
        try:
            temp = []
            for data in chain_data:
                block = Block(data['index'], data['transactions'], data['previous_hash'], self.difficulty)
                block.timestamp = data['timestamp']
                block.nonce = data['nonce']
                block.hash = block.compute_hash()
                if block.hash != data['hash']:
                    return False
                temp.append(block)
            return True
        except:
            return False

    # Transforme un dictionnaire en objet Block (utile pour les chaînes synchronisées)
    def dict_to_block(self, data):
        block = Block(data['index'], data['transactions'], data['previous_hash'], self.difficulty)
        block.timestamp = data['timestamp']
        block.nonce = data['nonce']
        block.hash = data['hash']
        block.merkle_root = data['merkle_root']
        return block


### ==== FLASK APP ==== ###
app = Flask(__name__)
blockchain = Blockchain(difficulty=3)
transaction_pool = []
peer_nodes = set()

### ==== HTML TEMPLATE ==== ###
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Blockchain Web</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial; padding: 20px; background-color: #f5f5f5; }
        .block { background: white; border: 1px solid #aaa; padding: 10px; margin: 10px 0; }
        .valid { color: green; }
        .invalid { color: red; }
        input, button { padding: 5px; margin-top: 5px; }
    </style>
</head>
<body>
    <h1>🧱 Mini Blockchain Web</h1>

    <form method="POST" action="/add_transaction">
        <input type="text" name="sender" placeholder="Expéditeur" required>
        <input type="text" name="receiver" placeholder="Destinataire" required>
        <button type="submit">📬 Ajouter transaction</button>
    </form>

    <form method="POST" action="/mine">
        <button>🪙 Miner</button>
    </form>

    <form method="POST" action="/attack">
        <button>🔥 Attaque 51%</button>
    </form>

    <form method="POST" action="/reset">
        <button>🔄 Réinitialiser</button>
    </form>

    <form method="POST" action="/register_node">
        <input type="text" name="node_url" placeholder="http://IP:port">
        <button>🔗 Ajouter nœud</button>
    </form>

    <form method="GET" action="/sync">
        <button>🔄 Synchroniser avec pairs</button>
    </form>

    <h3>Status de la chaîne: {% if valid %}<span class="valid">Valide ✅</span>{% else %}<span class="invalid">Corrompue ❌</span>{% endif %}</h3>

    <canvas id="chainChart" width="600" height="200"></canvas>
    <script>
        const ctx = document.getElementById('chainChart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: {{ labels }},
                datasets: [{
                    label: 'Croissance de la chaîne',
                    data: {{ sizes }},
                    backgroundColor: 'rgba(0, 123, 255, 0.2)',
                    borderColor: 'rgba(0, 123, 255, 1)',
                    borderWidth: 1,
                    fill: true
                }]
            },
            options: { scales: { y: { beginAtZero: true } } }
        });
    </script>

    {% for block in chain %}
        <div class="block">
            <b>Bloc {{ block.index }}</b><br>
            Hash: {{ block.hash[:20] }}...<br>
            Précédent: {{ block.previous_hash[:20] }}...<br>
            Merkle: {{ block.merkle_root[:20] }}...<br>
            Transactions: <ul>{% for tx in block.transactions %}<li>{{ tx }}</li>{% endfor %}</ul>
        </div>
    {% endfor %}
</body>
</html>
"""

@app.route('/')
def index():
    labels = list(range(len(blockchain.chain)))
    sizes = list(range(1, len(blockchain.chain)+1))
    return render_template_string(HTML,
        chain=blockchain.chain,
        valid=blockchain.is_valid(),
        labels=labels,
        sizes=sizes
    )

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    sender = request.form['sender']
    receiver = request.form['receiver']
    transaction_pool.append(f"{sender} -> {receiver}")
    return redirect(url_for('index'))

@app.route('/mine', methods=['POST'])
def mine():
    if not transaction_pool:
        transaction_pool.append("System -> Miner")
    blockchain.add_block(transaction_pool.copy())
    transaction_pool.clear()
    return redirect(url_for('index'))

@app.route('/attack', methods=['POST'])
def attack():
    if len(blockchain.chain) > 1:
        blockchain.chain[-1].transactions[0] = "Attacker -> Attacker"
        blockchain.chain[-1].hash = blockchain.chain[-1].compute_hash()
    return redirect(url_for('index'))

@app.route('/reset', methods=['POST'])
def reset():
    global blockchain, transaction_pool
    blockchain = Blockchain(difficulty=3)
    transaction_pool = []
    return redirect(url_for('index'))

@app.route('/chain')
def get_chain():
    return jsonify([b.to_dict() for b in blockchain.chain])

@app.route('/register_node', methods=['POST'])
def register_node():
    url = request.form['node_url']
    if url:
        peer_nodes.add(url)
    return redirect(url_for('index'))

@app.route('/sync')
def sync():
    for node in list(peer_nodes):
        try:
            r = requests.get(f"{node}/chain")
            new_chain = r.json()
            blockchain.replace_chain(new_chain)
        except:
            continue
    return redirect(url_for('index'))

### === MAIN === ###
if __name__ == "__main__":
    app.run(debug=True, port=5000)
