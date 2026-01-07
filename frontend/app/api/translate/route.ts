import { NextRequest, NextResponse } from 'next/server';

/**
 * 翻译文本
 * POST /api/translate
 *
 * 支持的翻译源：
 * - deeplx: DeepL 免费 API (通过 load balancer)
 * - mock: 模拟翻译（开发用）
 */

interface TranslateRequest {
  text: string;
  sourceLang?: string;
  targetLang?: string;
  service?: 'deeplx' | 'mock';
}

interface TranslateResponse {
  translatedText: string;
  detectedLang?: string;
  service: string;
}

// DeepL 免费 API 端点列表（负载均衡）
const DEEPLX_ENDPOINTS = [
  'https://api.deeplx.org/translate',
  'https://deeplx.missuo.ru/translate',
];

async function translateWithDeepLX(
  text: string,
  sourceLang: string,
  targetLang: string
): Promise<{ text: string; detectedLang?: string }> {
  // 随机选择一个端点
  const endpoint = DEEPLX_ENDPOINTS[Math.floor(Math.random() * DEEPLX_ENDPOINTS.length)];

  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text,
      source_lang: sourceLang.toUpperCase(),
      target_lang: targetLang.toUpperCase(),
    }),
  });

  if (!response.ok) {
    throw new Error(`DeepLX API error: ${response.status}`);
  }

  const data = await response.json();

  if (data.code !== 200) {
    throw new Error(data.message || 'Translation failed');
  }

  return {
    text: data.data || data.alternatives?.[0] || '',
    detectedLang: data.source_lang,
  };
}

function mockTranslate(text: string): string {
  // 简单的模拟翻译：添加前缀
  return `[翻译] ${text.slice(0, 50)}${text.length > 50 ? '...' : ''}`;
}

export async function POST(request: NextRequest) {
  try {
    const body: TranslateRequest = await request.json();
    const {
      text,
      sourceLang = 'auto',
      targetLang = 'ZH',
      service = 'deeplx',
    } = body;

    if (!text || typeof text !== 'string') {
      return NextResponse.json(
        { error: '请提供要翻译的文本' },
        { status: 400 }
      );
    }

    if (text.length > 5000) {
      return NextResponse.json(
        { error: '文本长度不能超过 5000 字符' },
        { status: 400 }
      );
    }

    let result: TranslateResponse;

    if (service === 'mock') {
      result = {
        translatedText: mockTranslate(text),
        service: 'mock',
      };
    } else {
      const { text: translatedText, detectedLang } = await translateWithDeepLX(
        text,
        sourceLang,
        targetLang
      );
      result = {
        translatedText,
        detectedLang,
        service: 'deeplx',
      };
    }

    return NextResponse.json(result);
  } catch (error) {
    console.error('翻译失败:', error);
    return NextResponse.json(
      { error: '翻译失败: ' + (error as Error).message },
      { status: 500 }
    );
  }
}

/**
 * 批量翻译
 * 用于翻译多个条目的标题和摘要
 */
export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    const { items, targetLang = 'ZH' } = body;

    if (!Array.isArray(items) || items.length === 0) {
      return NextResponse.json(
        { error: '请提供要翻译的条目列表' },
        { status: 400 }
      );
    }

    const results = await Promise.allSettled(
      items.map(async (item: { title?: string; abstract?: string; id: string }) => {
        const translations: { titleZh?: string; abstractZh?: string } = {};

        if (item.title) {
          try {
            const { text } = await translateWithDeepLX(item.title, 'auto', targetLang);
            translations.titleZh = text;
          } catch {
            translations.titleZh = undefined;
          }
        }

        if (item.abstract) {
          try {
            const { text } = await translateWithDeepLX(item.abstract, 'auto', targetLang);
            translations.abstractZh = text;
          } catch {
            translations.abstractZh = undefined;
          }
        }

        return { id: item.id, ...translations };
      })
    );

    const translations = results.map((result, index) => {
      if (result.status === 'fulfilled') {
        return result.value;
      }
      return { id: items[index].id, error: 'Translation failed' };
    });

    return NextResponse.json({ translations });
  } catch (error) {
    console.error('批量翻译失败:', error);
    return NextResponse.json(
      { error: '批量翻译失败: ' + (error as Error).message },
      { status: 500 }
    );
  }
}

