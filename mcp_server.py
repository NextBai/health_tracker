from mcp.server.fastmcp import FastMCP
from models.database import get_user_by_id, get_recent_bps, get_recent_postures

mcp = FastMCP("HealthTracker")

@mcp.tool()
def get_user_profile(user_id: int) -> str:
    """獲取使用者的基本資料 (身高, 體重, 年齡, 職業等)"""
    user = get_user_by_id(user_id)
    if not user:
        return "User not found."
    return f"年齡: {user['age']}, 性別: {user['gender']}, 身高: {user['height']}cm, 體重: {user['weight']}kg, 職業: {user['occupation']}"

@mcp.tool()
def get_user_bp_records(user_id: int, limit: int = 10) -> str:
    """獲取使用者近期的血壓與心率紀錄"""
    bps = get_recent_bps(user_id, limit=limit)
    if not bps:
        return "尚無血壓紀錄。"
    res = []
    for b in bps:
        res.append(f"時間: {b['timestamp']}, 收縮壓: {b['systolic']}, 舒張壓: {b['diastolic']}, 心率: {b['heart_rate']}")
    return "\n".join(res)

@mcp.tool()
def get_user_posture_records(user_id: int, limit: int = 5) -> str:
    """獲取使用者近期的姿勢分析結果 (如高低肩、駝背、骨盆傾斜等)"""
    postures = get_recent_postures(user_id, limit=limit)
    if not postures:
        return "尚無姿勢紀錄。"
    res = []
    for p in postures:
        res.append(f"時間: {p['timestamp']}, 指標: {p['metrics']}")
    return "\n".join(res)

if __name__ == "__main__":
    mcp.run()
