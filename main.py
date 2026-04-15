import os
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# --- CONFIGURACIÓN ---
# Render leerá esto de la sección "Environment"
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))  # Configura tu ID en Render también

# --- SISTEMA DE BASE DE DATOS (SQLite) ---

def init_db():
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
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
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO usuarios (user_id, saldo) VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET saldo = saldo + ?
    ''', (user_id, cantidad, cantidad))
    conn.commit()
    conn.close()

# --- TECLADOS ---

def get_main_keyboard():
    return ReplyKeyboardMarkup([
        ["📦 Ver disponibilidad", "💰 Comprar plan"],
        ["📋 Mis Planes", "💰 Mi Balance", "Admin"],
        ["🎁 Bono Prueba (+100)"]  # Botón solicitado
    ], resize_keyboard=True)

def get_plans_keyboard():
    return ReplyKeyboardMarkup([
        ["Comprar 10 USD", "Comprar 20 USD"],
        ["Comprar 50 USD", "Comprar 100 USD"],
        ["🔙 Volver"]
    ], resize_keyboard=True)

# --- MANEJADORES ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    update_saldo(user_id, 0) # Asegura que el usuario exista en la DB
    
    await update.message.reply_text(
        "👋 *Bienvenido al Bot de Inversiones*\n\nUsa el menú inferior para navegar.",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    saldo_actual = get_saldo(user_id)

    # 1. MOSTRAR SALDO ACTUAL
    if text == "💰 Mi Balance":
        await update.message.reply_text(
            f"💰 *ESTADO DE CUENTA*\n\n💵 Saldo disponible: *{saldo_actual:.2f} USD*",
            parse_mode="Markdown"
        )

    # 2. BOTÓN DE PRUEBA (+100)
    elif text == "🎁 Bono Prueba (+100)":
        update_saldo(user_id, 100.0)
        nuevo_saldo = get_saldo(user_id)
        await update.message.reply_text(f"✅ ¡Se han añadido 100 USD de prueba!\n💰 Nuevo saldo: *{nuevo_saldo:.2f} USD*", parse_mode="Markdown")

    # 3. MENÚ DE COMPRA
    elif text == "💰 Comprar plan":
        await update.message.reply_text("Selecciona el plan que deseas adquirir:", reply_markup=get_plans_keyboard())

    # 4. LÓGICA DE DESCUENTO DE SALDO
    elif text.startswith("Comprar ") and "USD" in text:
        # Extraer el número del texto (ej: "Comprar 10 USD" -> 10)
        try:
            costo = float(text.split(" ")[1])
            if saldo_actual >= costo:
                update_saldo(user_id, -costo) # Descontar
                await update.message.reply_text(
                    f"✅ *Compra exitosa*\nHas adquirido el plan de {costo} USD.\n\n💰 Saldo restante: *{get_saldo(user_id):.2f} USD*",
                    parse_mode="Markdown",
                    reply_markup=get_main_keyboard()
                )
            else:
                await update.message.reply_text(f"❌ *Saldo insuficiente*\nNecesitas {costo} USD y solo tienes {saldo_actual:.2f} USD.", parse_mode="Markdown")
        except:
            await update.message.reply_text("Error al procesar la compra.")

    elif text == "🔙 Volver":
        await update.message.reply_text("Volviendo al menú principal...", reply_markup=get_main_keyboard())

    elif text == "Admin":
        if user_id == ADMIN_ID:
            await update.message.reply_text("🔐 Panel Admin - (Aquí puedes añadir tus funciones de gestión)")
        else:
            await update.message.reply_text("❌ No tienes permisos.")

# --- EJECUCIÓN ---

if __name__ == '__main__':
    init_db()
    
    if not TOKEN:
        print("ERROR: No se encontró la variable TELEGRAM_TOKEN")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
        
        print("Bot iniciado correctamente...")
        app.run_polling()