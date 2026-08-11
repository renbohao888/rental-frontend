<template>
  <div class="ai-assistant">
    <!-- 悬浮球（挂在页面边框右下角） -->
    <div class="ai-fab" :class="{ active: open }" @click="toggle" title="租赁助手">
      <span class="fab-icon">{{ open ? '✕' : '🤖' }}</span>
      <span v-if="!open" class="fab-tip">租赁助手</span>
    </div>

    <!-- 小型聊天框 -->
    <transition name="ai-pop">
      <div v-if="open" class="ai-panel">
        <div class="ai-header">
          <div class="ai-title">
            <div class="ai-logo">🤖</div>
            <div class="ai-meta">
              <div class="ai-name">租赁助手</div>
              <div class="ai-status">
                <span class="dot" :class="{ thinking }"></span>
                {{ thinking ? '正在思考…' : '在线 · 平台房源都在我脑中' }}
              </div>
            </div>
          </div>
          <el-button text class="ai-min" @click="open = false">—</el-button>
        </div>

        <div class="ai-messages" ref="msgBoxRef">
          <div v-for="(msg, i) in messages" :key="i" class="ai-msg" :class="msg.role">
            <div v-if="msg.role === 'assistant'" class="msg-avatar">🤖</div>
            <div class="msg-body">
              <div class="msg-bubble" :class="{ user: msg.role === 'user' }">
                <template v-if="msg.role === 'assistant'">
                  <span class="msg-text">{{ msg.displayed }}</span>
                  <span v-if="msg.typing" class="cursor">▍</span>
                </template>
                <template v-else>{{ msg.content }}</template>
              </div>

              <!-- 推荐房源卡片 -->
              <div v-if="msg.rooms && msg.rooms.length" class="msg-rooms">
                <div class="ai-room" v-for="room in msg.rooms" :key="room.id" @click="goRoom(room.id)">
                  <img class="ai-room-cover" :src="room.cover || placeholder(room.id)" alt="" />
                  <div class="ai-room-info">
                    <div class="ai-room-title">{{ room.title }}</div>
                    <div class="ai-room-addr">{{ room.address }}</div>
                    <div class="ai-room-price">¥{{ room.price }}<span>/晚</span></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 快捷问题 -->
        <div class="ai-suggests">
          <span v-for="s in suggests" :key="s" class="ai-suggest" @click="send(s)">{{ s }}</span>
        </div>

        <div class="ai-input-row">
          <el-input
            v-model="input"
            placeholder="告诉我您的找房需求…"
            maxlength="200"
            clearable
            :disabled="thinking"
            @keyup.enter="send()"
          />
          <el-button type="primary" :loading="thinking" :disabled="!input.trim()" @click="send()">
            发送
          </el-button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { aiChat } from '@/api/ai'

const router = useRouter()
const open = ref(false)
const input = ref('')
const thinking = ref(false)
const messages = ref([])
const msgBoxRef = ref(null)
let greeted = false

const suggests = ['帮我推荐房源', '1000元以内的房源', '两室一厅', '天河区', '近地铁']

const placeholder = (id) => `https://loremflickr.com/300/200/house?random=${id}`


// 打字机效果：逐字"跳"出来，边思考边回答的观感
const typewriter = async (msg, text) => {
  msg.displayed = ''
  msg.typing = true
  const chars = Array.from(text)
  for (let i = 0; i < chars.length; i += 1) {
    msg.displayed += chars[i]
    scrollBottom()
    const ch = chars[i]
    // 标点/换行处稍作停顿，模拟真实思考节奏
    const gap = ch === '\n' ? 100 : /[，。！？、；：]/.test(ch) ? 45 : 18
    await sleep(gap)
  }
  msg.typing = false
  scrollBottom()
}

const pushAssistant = (reply, rooms) => {
  const msg = { role: 'assistant', displayed: '', content: reply, typing: false, rooms: rooms || [] }
  messages.value.push(msg)
  scrollBottom()
  return msg
}

const toggle = () => {
  open.value = !open.value
  if (open.value && !greeted) {
    greeted = true
    // 首次打开：主动打招呼并加载热门房源
    thinking.value = true
    scrollBottom()
    aiChat('你好')
      .then(async (res) => {
        const data = res?.data || {}
        const reply = data.reply || '您好呀！我是「租赁助手」，想找什么样的房子？'
        thinking.value = false
        const msg = pushAssistant(reply, data.rooms)
        await sleep(450) // 思考片刻
        await typewriter(msg, reply)
      })
      .catch(() => {
        thinking.value = false
        pushAssistant('您好，我是「租赁助手」🤖 不过服务暂时繁忙，请稍后再试试～', [])
      })
  }
}

const send = async (preset) => {
  const text = (preset || input.value).trim()
  if (!text || thinking.value) return
  input.value = ''
  messages.value.push({ role: 'user', content: text })
  scrollBottom()
  thinking.value = true
  try {
    const res = await aiChat(text)
    const data = res?.data || {}
    const reply = data.reply || '抱歉，我暂时没想好怎么回答，换个说法试试？'
    thinking.value = false
    const msg = pushAssistant(reply, data.rooms)
    await sleep(450) // 模拟"思考中"
    await typewriter(msg, reply)
  } catch (error) {
    thinking.value = false
    pushAssistant('抱歉，我连接服务有点慢～请稍后再试，或者先到「找房源」页面看看。', [])
  }
}

const goRoom = (id) => {
  router.push(`/room/${id}`)
}
</script>

<style scoped>
.ai-assistant {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 3000;
}

/* ===== 悬浮球 ===== */
.ai-fab {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff8b3d, #ff6a00);
  color: #fff;
  font-size: 26px;
  cursor: pointer;
  box-shadow: 0 6px 20px rgba(255, 106, 0, 0.45);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  margin-left: auto;
}
.ai-fab:hover {
  transform: scale(1.08) rotate(6deg);
  box-shadow: 0 8px 26px rgba(255, 106, 0, 0.55);
}
.ai-fab.active {
  transform: scale(1.05);
  background: linear-gradient(135deg, #555, #333);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
}
.fab-tip {
  font-size: 12px;
  background: rgba(0, 0, 0, 0.65);
  color: #fff;
  padding: 4px 8px;
  border-radius: 10px;
  position: absolute;
  right: 62px;
  top: 50%;
  transform: translateY(-50%);
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease;
}
.ai-fab:hover .fab-tip {
  opacity: 1;
}

/* ===== 聊天面板 ===== */
.ai-panel {
  position: fixed;
  right: 24px;
  bottom: 92px;
  width: 380px;
  max-height: 620px;
  height: min(620px, calc(100vh - 140px));
  display: flex;
  flex-direction: column;
  background: var(--bg-card);
  color: var(--text-main);
  border: 1px solid var(--border-color);
  border-radius: 18px;
  box-shadow: 0 16px 48px var(--shadow-color);
  overflow: hidden;
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* 弹出动画 */
.ai-pop-enter-active,
.ai-pop-leave-active {
  transition: opacity 0.28s ease, transform 0.28s ease;
}
.ai-pop-enter-from,
.ai-pop-leave-to {
  opacity: 0;
  transform: translateY(24px) scale(0.94);
}

.ai-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background: linear-gradient(135deg, #ff8b3d, #ff6a00);
  color: #fff;
}
.ai-title {
  display: flex;
  align-items: center;
  gap: 10px;
}
.ai-logo {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}
.ai-name {
  font-size: 15px;
  font-weight: 700;
}
.ai-status {
  font-size: 11px;
  opacity: 0.9;
  display: flex;
  align-items: center;
  gap: 4px;
}
.ai-status .dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #7cffb2;
  display: inline-block;
}
.ai-status .dot.thinking {
  background: #ffe08a;
  animation: ai-blink 0.8s infinite alternate;
}
@keyframes ai-blink {
  from { opacity: 1; }
  to { opacity: 0.2; }
}
.ai-min {
  color: #fff !important;
  font-size: 16px;
}

/* ===== 消息区 ===== */
.ai-messages {
  flex: 1;
  overflow-y: auto;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.ai-msg {
  display: flex;
  gap: 8px;
  max-width: 100%;
}
.ai-msg.user {
  justify-content: flex-end;
}
.msg-avatar {
  flex-shrink: 0;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff8b3d, #ff6a00);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
}
.msg-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 82%;
}
.msg-bubble {
  background: var(--bg-soft);
  border: 1px solid var(--border-color);
  color: var(--text-main);
  border-radius: 14px 14px 14px 4px;
  padding: 10px 12px;
  font-size: 13px;
  line-height: 1.65;
  white-space: pre-wrap;
  word-break: break-word;
  box-shadow: 0 1px 3px var(--shadow-color);
}
.msg-bubble.user {
  background: linear-gradient(135deg, #ff8b3d, #ff6a00);
  color: #fff;
  border: none;
  border-radius: 14px 14px 4px 14px;
}
.cursor {
  display: inline-block;
  color: #ff6a00;
  animation: ai-blink 0.7s infinite;
  font-weight: 700;
}

/* ===== 推荐房源卡片 ===== */
.msg-rooms {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 2px;
}
.ai-room {
  display: flex;
  gap: 10px;
  align-items: center;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 8px;
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}
.ai-room:hover {
  border-color: #ff6a00;
  box-shadow: 0 4px 14px var(--shadow-strong);
  transform: translateY(-1px);
}
.ai-room-cover {
  width: 56px;
  height: 46px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
}
.ai-room-info {
  flex: 1;
  min-width: 0;
}
.ai-room-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.ai-room-addr {
  font-size: 11px;
  color: var(--text-sub);
  margin: 2px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.ai-room-price {
  font-size: 14px;
  font-weight: 700;
  color: #ff6a00;
}
.ai-room-price span {
  font-size: 11px;
  font-weight: 400;
  color: var(--text-sub);
}

/* ===== 快捷问题 ===== */
.ai-suggests {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 8px 14px 0;
}
.ai-suggest {
  font-size: 11px;
  color: #ff6a00;
  background: var(--bg-soft);
  border: 1px solid rgba(255, 106, 0, 0.35);
  border-radius: 12px;
  padding: 4px 10px;
  cursor: pointer;
  transition: background 0.2s ease;
}
.ai-suggest:hover {
  background: rgba(255, 106, 0, 0.12);
}

/* ===== 输入区 ===== */
.ai-input-row {
  display: flex;
  gap: 8px;
  padding: 10px 14px 14px;
}
</style>


