from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)

def format_number(num):
    # Membatasi angka hingga 10 digit di belakang koma, kemudian menghapus angka nol di belakang koma
    return "{:.3f}".format(num).rstrip('0').rstrip('.')  # Membatasi 10 angka desimal, lalu hapus nol yang tidak perlu

def calculate_mm2_queue(lambda_, mu, arrival_time, service_time):
    rho = lambda_ / (2 * mu)
    
    # Validasi stabilitas sistem
    if rho >= 1:
        raise ValueError("Sistem tidak stabil: ρ (utilisasi per server) harus lebih kecil dari 1.")
    
    # Hitung W (waktu rata-rata dalam sistem)
    W = 1 / (mu - (lambda_ / 2))
    
    # Hitung Wq (waktu rata-rata dalam antrian)
    Wq = (lambda_ / (2 * mu * (mu - (lambda_ / 2))))

    # Format hasil perhitungan agar angka nol di belakang koma hilang
    lambda_str = format_number(lambda_)
    mu_str = format_number(mu)
    rho_str = format_number(rho)
    W_str = format_number(W)
    Wq_str = format_number(Wq)

    # Langkah-langkah perhitungan, menampilkan input asli tanpa format desimal
    steps = [
        f"Langkah 1: Hitung λ (Laju kedatangan)<br>"
        f"$$λ = \\frac{{1}}{{\\text{{waktu antar kedatangan}}}} = \\frac{{1}}{{{arrival_time}}} = {lambda_str}$$",
        f"Langkah 2: Hitung μ (Laju pelayanan per pelayan)<br>"
        f"$$μ = \\frac{{1}}{{\\text{{waktu pelayanan per pelayan}}}} = \\frac{{1}}{{{service_time}}} = {mu_str}$$",
        f"Langkah 3: Hitung pemanfaatan pelayan (ρ)<br>"
        f"$$ρ = \\frac{{λ}}{{2μ}} = \\frac{{{lambda_str}}}{{2 \\cdot {mu_str}}} = {rho_str}$$",
        f"Langkah 4: Hitung waktu rata-rata dalam sistem (W)<br>"
        f"$$W = \\frac{{1}}{{μ - \\frac{{λ}}{{2}}}} = \\frac{{1}}{{{mu_str} - \\frac{{{lambda_str}}}{{2}}}} = {W_str}$$",
        f"Langkah 5: Hitung waktu rata-rata dalam antrian (Wq)<br>"
        f"$$Wq = \\frac{{λ}}{{2μ (μ - \\frac{{λ}}{{2}})}} = \\frac{{{lambda_str}}}{{2 \\cdot {mu_str} \\cdot ({mu_str} - \\frac{{{lambda_str}}}{{2}})}} = {Wq_str}$$"
    ]
    
    return {"W": W, "Wq": Wq, "lambda": lambda_, "mu": mu, "rho": rho}, steps

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        arrival_time = float(request.form['arrival_time'])  # Waktu antar kedatangan (dalam menit)
        service_time = float(request.form['service_time'])  # Waktu pelayanan per pelayan (dalam menit)

        # Menghitung λ dan μ
        lambda_ = 1 / arrival_time  # Rata-rata kedatangan (per menit)
        mu = 1 / service_time      # Rata-rata pelayanan (per menit)

        # Validasi ρ
        rho = lambda_ / (2 * mu)
        if rho >= 1:
            return jsonify({'error': "Sistem tidak stabil: ρ (utilisasi per server) harus lebih kecil dari 1."})

        result, steps = calculate_mm2_queue(lambda_, mu, arrival_time, service_time)
        return jsonify({
            'result': result,
            'steps': steps
        })
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)