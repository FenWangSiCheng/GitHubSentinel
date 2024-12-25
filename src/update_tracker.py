from typing import Dict, List, Any
import logging
from datetime import datetime
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

class UpdateTracker:
    def __init__(self, config: Dict[str, Any]):
        """
        初始化更新追踪器
        
        Args:
            config: 数据库配置信息
        """
        self.config = config
        self.db_path = Path(config.get('path', 'data/sentinel.db'))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        
    def _init_db(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建更新记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS updates (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    repo_owner TEXT NOT NULL,
                    repo_name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT,
                    author TEXT,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP,
                    url TEXT,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_updates_repo 
                ON updates(repo_owner, repo_name)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_updates_type 
                ON updates(type)
            ''')
            
            conn.commit()
            
    def filter_new_updates(self, updates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        过滤出新的更新
        
        Args:
            updates: 更新列表
            
        Returns:
            List[Dict[str, Any]]: 新的更新列表
        """
        new_updates = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for update in updates:
                # 检查更新是否已存在
                cursor.execute(
                    'SELECT id FROM updates WHERE id = ? AND type = ?',
                    (str(update['id']), update['type'])
                )
                
                if cursor.fetchone() is None:
                    new_updates.append(update)
                    
        return new_updates
        
    def mark_as_processed(self, updates: List[Dict[str, Any]]):
        """
        将更新标记为已处理
        
        Args:
            updates: 更新列表
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for update in updates:
                try:
                    cursor.execute('''
                        INSERT INTO updates (
                            id, type, repo_owner, repo_name, title,
                            content, author, created_at, updated_at, url
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        str(update['id']),
                        update['type'],
                        update.get('owner', ''),
                        update.get('repo', ''),
                        update.get('title', ''),
                        update.get('message', update.get('body', '')),
                        update.get('author', ''),
                        update.get('date'),
                        update.get('updated_at'),
                        update.get('url', '')
                    ))
                    
                except sqlite3.IntegrityError:
                    logger.warning(f"Update {update['id']} already exists in database")
                    continue
                    
            conn.commit()
            
    def get_processed_updates(
        self,
        repo_owner: str = None,
        repo_name: str = None,
        update_type: str = None,
        since: datetime = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取已处理的更新
        
        Args:
            repo_owner: 仓库所有者
            repo_name: 仓库名称
            update_type: 更新类型
            since: 起始时间
            limit: 返回结果数量限制
            
        Returns:
            List[Dict[str, Any]]: 更新列表
        """
        query = 'SELECT * FROM updates WHERE 1=1'
        params = []
        
        if repo_owner:
            query += ' AND repo_owner = ?'
            params.append(repo_owner)
        if repo_name:
            query += ' AND repo_name = ?'
            params.append(repo_name)
        if update_type:
            query += ' AND type = ?'
            params.append(update_type)
        if since:
            query += ' AND created_at >= ?'
            params.append(since)
            
        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            return [dict(row) for row in cursor.fetchall()]
            
    def clear_old_updates(self, days: int = 30):
        """
        清理旧的更新记录
        
        Args:
            days: 保留最近几天的记录
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM updates WHERE processed_at < datetime("now", ?)',
                (f'-{days} days',)
            )
            conn.commit()
            
        logger.info(f"Cleared updates older than {days} days")
        
    def get_statistics(
        self,
        repo_owner: str = None,
        repo_name: str = None,
        since: datetime = None
    ) -> Dict[str, Any]:
        """
        获取更新统计信息
        
        Args:
            repo_owner: 仓库所有者
            repo_name: 仓库名称
            since: 起始时间
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        query = '''
            SELECT 
                type,
                COUNT(*) as count,
                MIN(created_at) as first_update,
                MAX(created_at) as last_update
            FROM updates
            WHERE 1=1
        '''
        params = []
        
        if repo_owner:
            query += ' AND repo_owner = ?'
            params.append(repo_owner)
        if repo_name:
            query += ' AND repo_name = ?'
            params.append(repo_name)
        if since:
            query += ' AND created_at >= ?'
            params.append(since)
            
        query += ' GROUP BY type'
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            stats = {
                'total': 0,
                'by_type': {}
            }
            
            for row in cursor.fetchall():
                row_dict = dict(row)
                stats['by_type'][row_dict['type']] = {
                    'count': row_dict['count'],
                    'first_update': row_dict['first_update'],
                    'last_update': row_dict['last_update']
                }
                stats['total'] += row_dict['count']
                
            return stats 