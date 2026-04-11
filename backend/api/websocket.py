from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Any, Optional
import json
import asyncio
from services.clustering_service import clustering_service


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[websocket] = {"use_case": None, "resolution": 8}
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            del self.active_connections[websocket]
    
    async def send_message(self, websocket: WebSocket, message: Dict[str, Any]):
        try:
            await websocket.send_json(message)
        except Exception:
            pass
    
    async def broadcast_progress(self, progress: float, message: str = ""):
        for websocket in self.active_connections:
            await self.send_message(websocket, {
                "type": "progress",
                "pct": progress,
                "message": message
            })


manager = ConnectionManager()


async def handle_websocket_message(websocket: WebSocket, message: Dict[str, Any]):
    action = message.get("action")
    
    if action == "subscribe_hex":
        resolution = message.get("resolution", 8)
        use_case = message.get("use_case")
        weights = message.get("weights")
        
        manager.active_connections[websocket]["resolution"] = resolution
        manager.active_connections[websocket]["use_case"] = use_case
        
        await manager.send_message(websocket, {
            "type": "status",
            "message": f"Computing hex grid at resolution {resolution}..."
        })
        
        hex_scores = await clustering_service.compute_hex_grid_scores(
            resolution=resolution,
            weights=weights,
            use_case=use_case
        )
        
        total = len(hex_scores)
        batch_size = max(1, total // 10)
        
        for i in range(0, total, batch_size):
            batch = hex_scores[i:i + batch_size]
            
            geojson_features = []
            for hex_data in batch:
                geojson_features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [hex_data["center_lng"], hex_data["center_lat"]]
                    },
                    "properties": {
                        "h3_index": hex_data["h3_index"],
                        "composite_score": hex_data["composite_score"],
                        "sub_scores": hex_data["sub_scores"]
                    }
                })
            
            await manager.send_message(websocket, {
                "type": "hex_data",
                "features": geojson_features,
                "batch": i // batch_size + 1,
                "total_batches": (total + batch_size - 1) // batch_size
            })
            
            progress = min((i + batch_size) / total * 100, 100)
            await manager.send_message(websocket, {
                "type": "progress",
                "pct": progress,
                "message": f"Processing {min(i + batch_size, total)}/{total} hexagons"
            })
        
        await manager.send_message(websocket, {
            "type": "complete",
            "message": f"Hex grid computation complete: {total} hexagons"
        })
    
    elif action == "ping":
        await manager.send_message(websocket, {"type": "pong"})


async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await handle_websocket_message(websocket, message)
            except json.JSONDecodeError:
                await manager.send_message(websocket, {
                    "type": "error",
                    "message": "Invalid JSON message"
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket)