# 📊 Bot de Inversiones en Telegram

Este proyecto implementa un **bot de Telegram** para la gestión de planes de inversión, con menús interactivos mediante teclados personalizados y un panel de administración.

## 🚀 Características

- Menú principal para clientes:
  - 📦 Ver disponibilidad
  - 💰 Comprar plan
  - 📋 Mis planes
  - 💰 Mi balance
  - ❓ Ayuda

- Panel de administración:
  - 📋 Todos los planes
  - 📊 Repartir pago
  - 📋 Órdenes pendientes
  - 📉 Descontar retiro
  - 💰 Balance general
  - ➕ Agregar saldo
  - 🔄 Reiniciar stock
  - ❓ Ayuda
  - 🔙 Salir del panel admin

- Soporte para **ReplyKeyboardMarkup** con menús dinámicos.
- Separación de lógica entre clientes y administrador.
- Ejemplo de manejo de comandos (`/start`, `/menu`, `/admin`) y mensajes de texto.

## 🛠️ Requisitos

- Python 3.9 o superior
- Librería [python-telegram-bot](https://python-telegram-bot.org/) versión 20+

Instalación de dependencias:

```bash
pip install python-telegram-bot --upgrade
