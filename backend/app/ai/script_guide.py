"""脚本生成问答式引导服务"""
from typing import Dict, Any, List, Optional
from app.ai.openai_service import openai_service


class ScriptGuideService:
    """脚本生成问答式引导服务"""

    def __init__(self):
        self.openai = openai_service

    async def start_guide(self, keywords: str, output_type: str) -> Dict[str, Any]:
        """开始问答式引导

        Args:
            keywords: 用户输入的关键词
            output_type: 输出类型 (image_set/single_image/video)

        Returns:
            Dict: 包含第一个问题和会话ID
        """
        system_prompt = """你是一个专业的创意脚本引导助手。
根据用户提供的关键词和输出类型，生成一系列问题来收集必要信息。
请以JSON格式返回问题列表。"""

        prompt = f"""用户想要创作：{output_type}
关键词：{keywords}

请生成3-5个问题来收集必要信息。根据输出类型：
- image_set: 询问人物角色、故事线、场景、清晰度、尺寸等
- single_image: 询问图片内容描述、风格、清晰度、尺寸等
- video: 询问人物/任务、故事线、场景、清晰度、时长等

返回JSON格式：
{{
    "questions": [
        {{"id": 1, "question": "问题内容", "type": "text", "required": true}},
        ...
    ]
}}"""

        result = await self.openai.generate(prompt, system_prompt=system_prompt)

        import json
        try:
            questions_data = json.loads(result["content"])
            questions = questions_data.get("questions", [])
        except:
            # 如果AI返回的不是标准JSON，使用默认问题
            questions = self._get_default_questions(output_type)

        return {
            "session_id": self._generate_session_id(),
            "keywords": keywords,
            "output_type": output_type,
            "questions": questions,
            "current_question": 0,
            "answers": {}
        }

    def _get_default_questions(self, output_type: str) -> List[Dict[str, Any]]:
        """获取默认问题列表"""
        if output_type == "image_set":
            return [
                {"id": 1, "question": "请描述主要的人物角色形象", "type": "text", "required": True},
                {"id": 2, "question": "请描述故事线或叙事脉络", "type": "text", "required": True},
                {"id": 3, "question": "请选择清晰度", "type": "select", "options": ["720p", "1080p", "2k", "4k"], "required": True},
                {"id": 4, "question": "请选择图片尺寸", "type": "select", "options": ["1280x720", "1920x1080", "2560x1440", "3840x2160"], "required": True},
                {"id": 5, "question": "请描述场景建议（可选）", "type": "text", "required": False},
                {"id": 6, "question": "请描述风格、色调等补充信息（可选）", "type": "text", "required": False}
            ]
        elif output_type == "single_image":
            return [
                {"id": 1, "question": "请详细描述图片内容", "type": "text", "required": True},
                {"id": 2, "question": "请选择图片尺寸", "type": "select", "options": ["1280x720", "1920x1080", "2560x1440", "3840x2160"], "required": True},
                {"id": 3, "question": "请选择清晰度", "type": "select", "options": ["720p", "1080p", "2k", "4k"], "required": True},
                {"id": 4, "question": "请描述风格、色调等补充信息（可选）", "type": "text", "required": False}
            ]
        elif output_type == "video":
            return [
                {"id": 1, "question": "请描述视频的主要人物或任务", "type": "text", "required": True},
                {"id": 2, "question": "请描述视频的故事线或叙事脉络", "type": "text", "required": True},
                {"id": 3, "question": "请选择清晰度", "type": "select", "options": ["720p", "1080p", "2k", "4k"], "required": True},
                {"id": 4, "question": "请输入视频时长（秒）", "type": "number", "required": True},
                {"id": 5, "question": "请描述场景建议（可选）", "type": "text", "required": False},
                {"id": 6, "question": "请描述风格、配乐等补充信息（可选）", "type": "text", "required": False}
            ]
        return []

    def _generate_session_id(self) -> str:
        """生成会话ID"""
        import uuid
        return uuid.uuid4().hex

    async def answer_question(
        self,
        session_data: Dict[str, Any],
        question_id: int,
        answer: str
    ) -> Dict[str, Any]:
        """回答问题

        Args:
            session_data: 会话数据
            question_id: 问题ID
            answer: 答案

        Returns:
            Dict: 更新后的会话数据
        """
        session_data["answers"][str(question_id)] = answer
        session_data["current_question"] = question_id

        questions = session_data.get("questions", [])
        next_question_idx = question_id

        if next_question_idx < len(questions):
            session_data["next_question"] = questions[next_question_idx]
            session_data["completed"] = False
        else:
            session_data["completed"] = True
            session_data["next_question"] = None

        return session_data

    async def generate_script_from_answers(
        self,
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """根据问答结果生成脚本

        Args:
            session_data: 会话数据

        Returns:
            Dict: 生成的脚本内容
        """
        keywords = session_data.get("keywords", "")
        output_type = session_data.get("output_type", "")
        answers = session_data.get("answers", {})
        questions = session_data.get("questions", [])

        # 构建问答对
        qa_pairs = []
        for q in questions:
            q_id = str(q["id"])
            if q_id in answers:
                qa_pairs.append(f"Q: {q['question']}\nA: {answers[q_id]}")

        qa_text = "\n\n".join(qa_pairs)

        system_prompt = """你是一个专业的创意脚本生成助手。
根据用户的关键词和问答内容，生成详细的创作脚本。
脚本应该包含：
1. 主题和风格描述
2. 场景描述（如果是视频或图片集）
3. 具体的视觉元素建议
4. 色调和氛围建议

请以结构化的文本格式返回脚本。"""

        prompt = f"""请根据以下信息生成创作脚本：

关键词：{keywords}
输出类型：{output_type}

用户回答：
{qa_text}

请生成一个完整的创作脚本。"""

        result = await self.openai.generate(prompt, system_prompt=system_prompt)

        # 提取参数
        parameters = self._extract_parameters(answers, output_type)

        return {
            "script": result["content"],
            "keywords": keywords,
            "output_type": output_type,
            "parameters": parameters,
            "answers": answers
        }

    def _extract_parameters(self, answers: Dict[str, str], output_type: str) -> Dict[str, Any]:
        """从答案中提取参数"""
        parameters = {}

        # 提取清晰度
        for key, value in answers.items():
            if "清晰度" in str(value) or value in ["720p", "1080p", "2k", "4k", "8k"]:
                parameters["clarity"] = value

            # 提取尺寸
            if "x" in str(value) and any(char.isdigit() for char in str(value)):
                try:
                    parts = value.split("x")
                    if len(parts) == 2:
                        parameters["width"] = int(parts[0])
                        parameters["height"] = int(parts[1])
                except:
                    pass

            # 提取时长
            if output_type == "video" and "时长" in str(key):
                try:
                    parameters["duration"] = int(value)
                except:
                    pass

        # 设置默认值
        if "clarity" not in parameters:
            parameters["clarity"] = "1080p"
        if "width" not in parameters:
            parameters["width"] = 1920
        if "height" not in parameters:
            parameters["height"] = 1080
        if output_type == "video" and "duration" not in parameters:
            parameters["duration"] = 30

        return parameters


script_guide_service = ScriptGuideService()
