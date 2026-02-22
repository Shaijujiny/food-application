import asyncio

from sqlalchemy import select

from app.database.postgresql import async_session
from app.models.main.notifications import TblNotifications
from app.models.main.orders import TblOrders
from app.models.main.users import TblUsers


async def main():
    async with async_session() as db:
        res = await db.execute(
            select(TblNotifications).where(TblNotifications.related_user_id.is_(None))
        )
        notifs = res.scalars().all()
        for n in notifs:
            print(f"checking notif {n.notif_id} {n.title}")

            # If it's an order
            if n.type.value == "NEW_ORDER" and "#" in n.message:
                order_id_str = n.message.split("#")[1].split(" ")[0]
                try:
                    order_id = int(order_id_str)
                    order_res = await db.execute(
                        select(TblOrders.user_id).where(TblOrders.ord_id == order_id)
                    )
                    user_id = order_res.scalar_one_or_none()
                    if user_id:
                        print(f"fixing order {order_id} -> user_id {user_id}")
                        n.related_user_id = user_id
                except Exception as e:
                    print("Error fixing order", e)

            elif n.type.value == "NEW_USER" and "customer registered: " in n.message:
                username = n.message.split("registered: ")[1].split(" (")[0]
                user_res = await db.execute(
                    select(TblUsers.usr_id).where(TblUsers.username == username)
                )
                user_id = user_res.scalar_one_or_none()
                if user_id:
                    print(f"fixing user {username} -> user_id {user_id}")
                    n.related_user_id = user_id

        await db.commit()
        print("Done backfilling!")


if __name__ == "__main__":
    asyncio.run(main())
