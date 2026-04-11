# TOKEN = "1884569938:AAFL9zZiYJYXXZAlyTPLKFnUHVlf9wg6nCk"
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# CONFIGURACIÓN
TOKEN = "1884569938:AAFL9zZiYJYXXZAlyTPLKFnUHVlf9wg6nCk"
ADMIN_ID = 123456789 

# --- CONSTRUCTORES DE TECLADOS (REPLY KEYBOARD) ---

def get_client_keyboard():
    # Cada lista interna es una fila de botones
    keyboard = [
        ["📦 Ver disponibilidad", "💰 Comprar plan"],
        ["📋 Mis Planes", "💰 Mi Balance", "Admin"],
        ["❓ Ayuda"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
def get_plans_keyboard():
    # Cada lista interna es una fila de botones
    keyboard = [
        ["10 USD", "20 USD","50 USD"],
        ["100 USD"],
        ["🔙 Volver"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
def get_admin_keyboard():
    keyboard = [
        ["📦 Ver disponibilidad", "💰 Comprar plan","📋 Todos los Planes"],
        ["📊 Repartir Pago", "📋 Órdenes Pendientes", "📉 Descontar Retiro"],
        ["💰 Balance General","➕ Agregar Saldo", "🔄 Reiniciar Stock"],
        ["❓ Ayuda"],
        ["🔙 Salir del Panel Admin"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- MANEJADORES DE COMANDOS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📊 *BOT DE INVERSIONES*\n\n*SU BALANCE PERSONAL:*\n💰 Disponible para retirar: 0 USD"
    await update.message.reply_text(
        text, 
        parse_mode="Markdown", 
        reply_markup=get_client_keyboard()
    )

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ No tienes autorización.")
        return
    
    text = "🔐 *PANEL DE CONTROL*\n\n*BALANCE GENERAL:* 0 USD"
    await update.message.reply_text(
        text, 
        parse_mode="Markdown", 
        reply_markup=get_admin_keyboard()
    )

# --- MANEJADOR DE TEXTO (PARA LOS BOTONES) ---

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    # Lógica para volver al menú de cliente desde el de admin
    if text == "🔙 Salir del Panel Admin":
        await update.message.reply_text("Volviendo al menú de cliente...", reply_markup=get_client_keyboard())
        return

    # Debug de acciones
    if user_id == ADMIN_ID:
        # Aquí puedes poner lógica específica para el admin comparando el texto
        if text == "📋 Órdenes Pendientes":
            await update.message.reply_text("DEBUG ADMIN: Mostrando órdenes... [RET-001, RET-002]")
        elif text == "📊 Repartir Pago":
            await update.message.reply_text("DEBUG ADMIN: Monto a repartir hoy:")
        else:
            await update.message.reply_text(f"DEBUG ADMIN: Ejecutando '{text}'")
    else:
        # Lógica para clientes
        if text == "💰 Mi Balance":
            await update.message.reply_text("💰 *SU BALANCE*\n\nDisponible: 47.85 USD\n\n(Escribe 'Retirar' para continuar)")
        if text == "Admin":
            await update.message.reply_text(
        text, 
        parse_mode="Markdown", 
        reply_markup=get_admin_keyboard()  
    )
        if text == "💰 Comprar plan":
            await update.message.reply_text(
        text, 
        parse_mode="Markdown", 
        reply_markup=get_plans_keyboard()
    )
        if text == "🔙 Volver":
            await update.message.reply_text("Volviendo al menú principal...", reply_markup=get_client_keyboard())
     
        else:
            await update.message.reply_text(f"DEBUG CLIENTE: Has pulsado '{text}'")

# --- EJECUCIÓN ---

app = ApplicationBuilder().token(TOKEN).build()

# Comandos
app.add_handler(CommandHandler(["start", "menu"], start))
app.add_handler(CommandHandler("admin", admin_panel))

# Manejador para los clics en los botones de la barra (que llegan como texto)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

print("Bot con menú inferior activo...")
app.run_polling()