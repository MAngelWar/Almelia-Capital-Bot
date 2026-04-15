import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# --- CONFIGURACIÓN ---
# RECOMENDACIÓN: Genera un nuevo token en @BotFather, el anterior quedó expuesto.
TOKEN = "1884569938:AAFL9zZiYJYXXZAlyTPLKFnUHVlf9wg6nCk"
ADMIN_ID = 123456789  # Reemplaza con tu ID real de Telegram

# --- GESTIÓN DE BASE DE DATOS (SQLite) ---

def init_db():
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    # Creamos la tabla si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            user_id INTEGER PRIMARY KEY,
            saldo REAL DEFAULT 0.0
        )
    ''')
    conn.commit()
    conn.close()

def get_saldo(user_id):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT saldo FROM usuarios WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0.0

def update_saldo(user_id, cantidad):
    """Suma o resta cantidad al saldo actual"""
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    # Insertamos si no existe, si existe sumamos al saldo
    cursor.execute('''
        INSERT INTO usuarios (user_id, saldo) VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET saldo = saldo + ?
    ''', (user_id, cantidad, cantidad))
    conn.commit()
    conn.close()

# --- CONSTRUCTORES DE TECLADOS ---

def get_client_keyboard():
    keyboard = [
        ["📦 Ver disponibilidad", "💰 Comprar plan"],
        ["📋 Mis Planes", "💰 Mi Balance", "Admin"],
        ["❓ Ayuda"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_plans_keyboard():
    keyboard = [
        ["10 USD", "20 USD", "50 USD"],
        ["100 USD"],
        ["🔙 Volver"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_keyboard():
    keyboard = [
        ["📦 Ver disponibilidad", "💰 Comprar plan", "📋 Todos los Planes"],
        ["📊 Repartir Pago", "📋 Órdenes Pendientes", "📉 Descontar Retiro"],
        ["💰 Balance General", "➕ Agregar Saldo", "🔄 Reiniciar Stock"],
        ["❓ Ayuda"],
        ["🔙 Salir del Panel Admin"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- MANEJADORES DE COMANDOS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # Aseguramos que el usuario esté en la DB al iniciar
    update_saldo(user_id, 0) 
    
    saldo = get_saldo(user_id)
    text = f"📊 *BOT DE INVERSIONES*\n\n*SU BALANCE PERSONAL:*\n💰 Disponible: {saldo} USD"
    await update.message.reply_text(
        text, 
        parse_mode="Markdown", 
        reply_markup=get_client_keyboard()
    )

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ No tienes autorización.")
        return
    
    text = "🔐 *PANEL DE CONTROL ADMIN*"
    await update.message.reply_text(
        text, 
        parse_mode="Markdown", 
        reply_markup=get_admin_keyboard()
    )

# Comando extra para que tú como admin puedas dar saldo a alguien
# Uso: /recargar ID_DEL_USUARIO CANTIDAD
async def recargar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        user_target = int(context.args[0])
        monto = float(context.args[1])
        update_saldo(user_target, monto)
        await update.message.reply_text(f"✅ Se han añadido {monto} USD al usuario {user_target}.")
    except:
        await update.message.reply_text("Uso: `/recargar ID monto`", parse_mode="Markdown")

# --- MANEJADOR DE TEXTO ---

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    # Lógica de navegación
    if text == "🔙 Salir del Panel Admin" or text == "🔙 Volver":
        await update.message.reply_text("Volviendo al menú...", reply_markup=get_client_keyboard())
        return

    if text == "Admin":
        if user_id == ADMIN_ID:
            await admin_panel(update, context)
        else:
            await update.message.reply_text("❌ Acceso denegado.")
        return

    # Lógica de Balance Virtual
    if text == "💰 Mi Balance":
        saldo = get_saldo(user_id)
        await update.message.reply_text(
            f"💰 *SU BALANCE*\n\nDisponible: {saldo} USD\n\n(Escribe 'Retirar' para continuar)", 
            parse_mode="Markdown"
        )
        return

    if text == "💰 Comprar plan":
        await update.message.reply_text("Seleccione un monto:", reply_markup=get_plans_keyboard())
        return

    # Lógica de Compra (Ejemplo para el botón de 10 USD)
    if text == "10 USD":
        saldo_actual = get_saldo(user_id)
        if saldo_actual >= 10:
            update_saldo(user_id, -10)
            nuevo_saldo = get_saldo(user_id)
            await update.message.reply_text(f"✅ Compra exitosa. Nuevo saldo: {nuevo_saldo} USD", reply_markup=get_client_keyboard())
        else:
            await update.message.reply_text("❌ Saldo insuficiente para este plan.")
        return

    # Respuesta por defecto para otros botones
    await update.message.reply_text(f"Has seleccionado: {text}")

# --- EJECUCIÓN ---

if __name__ == '__main__':
    # Inicializar base de datos
    init_db()
    
    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler(["start", "menu"], start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("recargar", recargar))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    print("Bot con SQLite activo...")
    app.run_polling()