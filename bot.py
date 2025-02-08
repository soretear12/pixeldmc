import discord
from discord.ext import commands
from discord.ext.commands import TextChannelConverter
from discord.ui import View, Button, Modal, TextInput, Select
import asyncio
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

GUILD_ID = 1308339157265027174  # Укажи ID сервера
TICKET_CHANNEL_ID = 1308340461861339150  # Канал, куда будут отправляться заявки
ADMIN_ROLE_ID = 1309011989326204998  # ID роли администратора
MANAGER_ROLE_ID = 1308395260594094110
CREATOR_ROLE_ID = 1308346593711362068
CATEGORY_ID = 1336049134733623296  # ID категории для заявок

intents = discord.Intents.default()
intents.members = True  # Даем доступ к участникам сервера
intents.messages = True
intents.message_content = True
intents.dm_messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Бот {bot.user} запущен и команды синхронизированы!")


class OrderForm(Modal):
    def __init__(self, service_type):
        super().__init__(title="Оформление заказа")
        self.service_type = service_type

        if service_type in ["Простой Пиксель-Арт", "Сложный Пиксель-Арт"]:
            self.format_type = TextInput(label="📐 Формат рисунка", required=True)
            self.outline = TextInput(label="✏ Обводка", required=True,
                                     placeholder="Да/Нет")
            self.details = TextInput(label="📜 Детали рисунка", required=True, style=discord.TextStyle.long)
            self.references = TextInput(label="📎 Референсы", required=False, placeholder="Описание")
            self.promo_code = TextInput(label="🎟 Промокод", required=False, placeholder="Если нет, оставьте пустым")

            self.add_item(self.format_type)
            self.add_item(self.outline)
            self.add_item(self.details)
            self.add_item(self.references)
            self.add_item(self.promo_code)

        elif service_type == "Стикер-Пак":
            self.outline = TextInput(label="✏ Обводка", required=False,
                                     placeholder="Если не требуется, оставьте пустым")
            self.details = TextInput(label="📜 Детали заказа", required=True, style=discord.TextStyle.long, placeholder="Опишите ваш заказ")
            self.references = TextInput(label="🎭 Свой скин", required=True, style=discord.TextStyle.long, placeholder="Ссылка на ваш скин на https://ru.namemc.com/")
            self.promo_code = TextInput(label="🎟 Промокод", required=False, placeholder="Если нет, оставьте пустым")

            self.add_item(self.outline)
            self.add_item(self.details)
            self.add_item(self.references)
            self.add_item(self.promo_code)

        elif service_type == "Скин":
            self.width_hands = TextInput(label='🤝 Вид скина (рук)', placeholder='slim (тонкие Alex)/ classic (Широкие Stive)', required=True)
            self.details = TextInput(label="📜 Детали заказа", required=True, style=discord.TextStyle.long, placeholder="Опишите ваш заказ")
            self.references = TextInput(label="Референсы", required=False, style=discord.TextStyle.long, placeholder="Если нету, можете оставить пустым")
            self.promo_code = TextInput(label="🎟 Промокод", required=False, placeholder="Если нет, оставьте пустым")

            self.add_item(self.width_hands)
            self.add_item(self.details)
            self.add_item(self.references)
            self.add_item(self.promo_code)

        elif service_type == "Рендер":
            self.details = TextInput(label="📜 Детали заказа", required=True, style=discord.TextStyle.long, placeholder="Опишите ваш заказ")
            self.references = TextInput(label="Референсы", required=False, style=discord.TextStyle.long,
                                        placeholder="Если нету, можете оставить пустым")
            self.promo_code = TextInput(label="🎟 Промокод", required=False, placeholder="Если нет, оставьте пустым")

            self.add_item(self.details)
            self.add_item(self.references)
            self.add_item(self.promo_code)

        elif service_type == "Аватар":
            self.outline = TextInput(label="✏ Обводка", required=False,
                                     placeholder="Если не требуется, оставьте пустым")
            self.details = TextInput(label="📜 Детали заказа", required=True, style=discord.TextStyle.long,
                                     placeholder="Опишите ваш заказ")
            self.references = TextInput(label="Референсы", required=False, style=discord.TextStyle.long,
                                        placeholder="Если нету, можете оставить пустым")
            self.promo_code = TextInput(label="🎟 Промокод", required=False, placeholder="Если нет, оставьте пустым")

            self.add_item(self.outline)
            self.add_item(self.details)
            self.add_item(self.references)
            self.add_item(self.promo_code)




    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        message_pay = "# 💰 Для подтверждения заказа, необходимо внести оплату. Оплатите заказ на ник TupyBro или на счет (#381185)"
        category = discord.utils.get(guild.categories, id=CATEGORY_ID)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.get_role(ADMIN_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.get_role(CREATOR_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.get_role(MANAGER_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(name=f"заказ-{interaction.user.display_name}",
                                                         category=category, overwrites=overwrites)

        embed = discord.Embed(title="Новая заявка на заказ 🎨", color=discord.Color.blue())
        embed.add_field(name="📌 Вид услуги", value=self.service_type, inline=False)

        if hasattr(self, 'format_type'):
            embed.add_field(name="📐 Формат рисунка", value=self.format_type.value, inline=False)
        if hasattr(self, 'outline'):
            embed.add_field(name="✏ Обводка", value=self.outline.value if self.outline.value else "Не указана", inline=False)
        if hasattr(self, 'width_hands'):
            embed.add_field(name="🤚 Вид скина", value=self.width_hands.value, inline=False)
        embed.add_field(name="📜 Детали заказа", value=self.details.value, inline=False)
        if hasattr(self, 'references'):
            embed.add_field(name="📎 Референсы", value=self.references.value if self.references.value else "Нет",
                            inline=False)
        embed.add_field(name="🎟 Промокод", value=self.promo_code.value if self.promo_code.value else "Нет",
                        inline=False)
        embed.set_footer(text=f"Заказчик: {interaction.user.display_name} ({interaction.user.id})")

        close_button = Button(label="Закрыть заявку", style=discord.ButtonStyle.danger)

        await ticket_channel.send(message_pay)


        async def close_ticket(interaction: discord.Interaction):
            if interaction.user.guild_permissions.manage_channels:
                await interaction.response.send_message("✅ Заявка закрыта и канал удален.", ephemeral=True)
                await ticket_channel.delete()
            else:
                await interaction.response.send_message("❌ У вас нет прав для закрытия заявки.", ephemeral=True)

        close_button.callback = close_ticket
        view = View()
        view.add_item(close_button)

        await ticket_channel.send(
            f"{interaction.guild.get_role(ADMIN_ROLE_ID).mention} {interaction.guild.get_role(CREATOR_ROLE_ID).mention} {interaction.guild.get_role(MANAGER_ROLE_ID).mention}, новая заявка!",
            embed=embed, view=view)
        await interaction.response.send_message(
            f"✅ Ваша заявка создана! Перейдите в канал {ticket_channel.mention} для обсуждения.", ephemeral=True)


class TicketButton(View):
    def __init__(self):
        super().__init__(timeout=None)  # Отключаем таймер, чтобы кнопка работала бесконечно

    @discord.ui.button(label="Создать тикет", style=discord.ButtonStyle.green, custom_id="persistent_ticket_button")
    async def create_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Выберите нужную вам услугу:", view=ServiceSelectionView(), ephemeral=True)


class ServiceSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Простой Пиксель-Арт", emoji="🖼"),
            discord.SelectOption(label="Сложный Пиксель-Арт", emoji="🖼"),
            discord.SelectOption(label="Стикер-Пак", emoji="🧩"),
            discord.SelectOption(label="Скин", emoji="🎭"),
            discord.SelectOption(label="Рендер", emoji="🎞"),
            discord.SelectOption(label="Аватар", emoji="👨‍🦲")
        ]
        super().__init__(placeholder="Выберите нужную вам услугу", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(OrderForm(self.values[0]))


class ServiceSelectionView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Отключаем таймер для всех представлений
        self.add_item(ServiceSelect())


@bot.command()
async def ticket(ctx):
    view = TicketButton()
    await ctx.send("Нажмите кнопку ниже, чтобы создать тикет:", view=view)


@bot.event
async def setup_hook():
    # Регистрируем кнопку при старте бота
    bot.add_view(TicketButton())  # Для работы после перезапуска бота



class ArtistSelectionView(View):
    def __init__(self, zakaz: discord.Member, channel: discord.TextChannel, message: discord.Message):
        super().__init__()
        self.zakaz = zakaz
        self.channel = channel
        self.message = message

    async def delete_message(self):
        if self.message:
            try:
                await self.message.delete()
            except discord.NotFound:
                pass  # Сообщение уже удалено

    @discord.ui.button(label="Derti", style=discord.ButtonStyle.primary)
    async def derti_callback(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()

        await interaction.followup.send(f"Вы выбрали <@{834483965409624084}> для заказа <@{self.zakaz.id}>.")

        member = interaction.guild.get_member(834483965409624084)
        if member is None:
            try:
                member = await interaction.guild.fetch_member(834483965409624084)
            except discord.NotFound:
                await interaction.followup.send("❌ Пользователь Derti не найден на сервере.")
                return

        try:
            await member.send(f"Теперь вы занимаетесь заказом <@{self.zakaz.id}>.")
            await asyncio.sleep(1)
            await member.send(f"Ознакомьтесь с заказом в канале {self.channel.mention}.")

            overwrite = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            await self.channel.set_permissions(member, overwrite=overwrite)

        except discord.Forbidden:
            await interaction.followup.send("❌ Бот не может отправить ЛС художнику Derti.")

        await self.delete_message()
        self.stop()

    @discord.ui.button(label="MILK AB", style=discord.ButtonStyle.success)
    async def milkab_callback(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()

        await interaction.followup.send(f"Вы выбрали <@{1070040412250714192}> для заказа <@{self.zakaz.id}>.")

        member = interaction.guild.get_member(1070040412250714192)
        if member is None:
            try:
                member = await interaction.guild.fetch_member(1070040412250714192)
            except discord.NotFound:
                await interaction.followup.send("❌ Пользователь MILK AB не найден на сервере.")
                return

        try:
            await member.send(f"Теперь вы занимаетесь заказом <@{self.zakaz.id}>.")
            await asyncio.sleep(1)
            await member.send(f"Ознакомьтесь с заказом в канале {self.channel.mention}.")

            overwrite = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            await self.channel.set_permissions(member, overwrite=overwrite)

        except discord.Forbidden:
            await interaction.followup.send("❌ Бот не может отправить ЛС художнику MILK AB.")

        await self.delete_message()
        self.stop()


@bot.tree.command(name='skinmaker', description='Выбор художника')
async def skinmaker(interaction: discord.Interaction, zakaz: discord.Member):
    await interaction.response.defer()
    role_admin_id = 1309011989326204998
    role_creator_id = 1308346593711362068

    if not any(role.id in [role_admin_id, role_creator_id] for role in interaction.user.roles):
        await interaction.response.send_message("❌ У вас нет прав использовать эту команду.", ephemeral=True)
        return

    # Используем ссылки на изображения
    embed1 = discord.Embed()
    embed1.set_image(url="https://media.discordapp.net/attachments/1233329242696323124/1337324435799019621/Derti.png?ex=67a707ef&is=67a5b66f&hm=b5aa3e9899829b3f13884ecd2f360a30556ba4e33ab42513d12dc1031019d067&=&format=webp&quality=lossless&width=910&height=910")

    embed2 = discord.Embed()
    embed2.set_image(url="https://media.discordapp.net/attachments/1233329242696323124/1337324436126306374/MILK_AB.png?ex=67a707ef&is=67a5b66f&hm=795b3debf25099ca025b9135a4da023e6e7c496c6924904ed488223b6f4c8182&=&format=webp&quality=lossless&width=910&height=910")

    message = await interaction.channel.send(
        f"<@{zakaz.id}>, выберите себе художника:",
        view=ArtistSelectionView(zakaz, interaction.channel, None),
        embeds=[embed1, embed2]
    )

    # Передаём сообщение в View для последующего удаления
    view = ArtistSelectionView(zakaz, interaction.channel, message)
    await message.edit(view=view)

@bot.tree.command(name='test', description='Тестирование бота')
async def test(interaction: discord.Interaction):
    await interaction.response.send_message('PixelDMC крутые услуги')  # ✅ Correct

@bot.tree.command(name='pay_summ', description="Цена за услугу")
@commands.has_any_role(ADMIN_ROLE_ID, MANAGER_ROLE_ID, CREATOR_ROLE_ID)
async def pay_summ(interaction: discord.Interaction):
    await interaction.response.send_message('Введите сумму:', ephemeral=True)

    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=60.0)
        ar = msg.content
        await interaction.followup.send(f'С вас {ar} ар. Реквизиты указаны в самом первом сообщении!', ephemeral=False)
    except asyncio.TimeoutError:
        await interaction.followup.send('Время ожидания истекло. Попробуйте снова.', ephemeral=True)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Бот {bot.user} запущен и команды синхронизированы!")

bot.run(TOKEN)