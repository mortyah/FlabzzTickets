import os

import disnake
from disnake.ui import View, string_select, role_select

from core import MainBot, post_request, DeleteMessageView, get_request


class ChooseSettingTypeModRolesView(View):

    options = [
        disnake.SelectOption(
            label="・Change Moderation",
            value="change_moderation",
            description="Изменить список модераторских ролей",
        ),
        disnake.SelectOption(
            label="・View Moderation",
            value="view_moderation",
            description="Вывести список модераторских ролей"
        )
    ]

    def __init__(self, bot: MainBot):
        super().__init__(timeout=None)
        self.bot = bot

    @string_select(
        placeholder="Меню выбора",
        custom_id="choose_setting_type_select",
        options=options
    )
    async def choose_setting_type_select(self, select: disnake.SelectMenu, inter: disnake.MessageInteraction):
        await inter.message.edit(view=self)
        if inter.values[0] == "change_moderation":
            embed = disnake.Embed(
                title="Выберите роли, которым необходимо изменить статус",
                colour=self.bot.invisible_colour
            )
            return await inter.response.edit_message(embed=embed, view=UpdateModerationRoles(self.bot))
        else:
            moderation_roles = await get_request(f"/{inter.guild.id}/tickets_moderation")
            moderation_roles = moderation_roles.get("roles")
            if len(moderation_roles) == 0:
                embed = disnake.Embed(
                    title="Тикет-модераторы отсутствуют!",
                    colour=self.bot.invisible_colour
                )
            embed = disnake.Embed(
                title="Список тикет-модераторов:",
                colour=self.bot.invisible_colour
            )
            for i, role in enumerate(moderation_roles):
                role = inter.guild.get_role(int(role[0]))
                role_members = [member.mention for member in role.members]
                temp = "`-`" if len(role_members) > 0 else "У этой роли отсутствуют участники"
                embed.add_field(
                    name=f"{i+1}. Роль: @{role.name}",
                    value=temp+"\n`-`".join(role_members),
                    inline=False
                )
            await inter.send(embed=embed, view=DeleteMessageView(self.bot))


class UpdateModerationRoles(View):
    def __init__(self, bot: MainBot):
        super().__init__(timeout=None)
        self.bot = bot

    @role_select(
        placeholder="Выберите роли",
        max_values=10,
        custom_id="update_moderation_roles_select"
    )
    async def update_moderation_roles_select(self, select: disnake.SelectMenu, inter: disnake.MessageInteraction):
        await inter.message.edit(view=self)
        roles_ids = [role_id for role_id in inter.values]
        await post_request(
            path=f"/{inter.guild.id}/tickets_moderation",
            post_data=[
                ", ".join(roles_ids)
            ]
        )
        embed = disnake.Embed(
            title="Изменение модераторов!",
            description=f"{inter.author.mention}, вы изменили список тикет-модераторов",
            colour=self.bot.invisible_colour
        )
        await inter.send(
            embed=embed,
            view=DeleteMessageView(self.bot)
        )