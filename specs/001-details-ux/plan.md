# Implementation Plan: 今日の運航情報ページ UX改善

**Branch**: `001-details-ux` | **Date**: 2026-03-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-details-ux/spec.md`

## Summary

`/details/today` の運航情報ページを改善する。主な変更点は3つ：(1) DetailsController のクエリを「今日以降」から「今日だけ」かつ「出発時刻昇順」に修正、(2) Twig テンプレートをリファクタリングしてステータスバッジ・方向サブタイトル・条件付き表示を実装、(3) styles.css にバッジスタイルと `suspend` ステータスクラスを追加。既存エンティティ・スキーマの変更は不要。

## Technical Context

**Language/Version**: PHP 8.x / Symfony (latest stable) + Twig
**Primary Dependencies**: Doctrine ORM (QueryBuilder), Twig auto-escape
**Storage**: MySQL 8.0（読み取り専用。スキーマ変更なし）
**Testing**: PHPUnit / Symfony WebTestCase
**Target Platform**: Web ブラウザ（デスクトップ + モバイル 375px+）
**Project Type**: Web アプリケーション（Symfony MVC）
**Performance Goals**: ページロードに特別な要件なし（既存と同等）
**Constraints**: スキーマ変更禁止、新サービスクラス不要（MVP原則）
**Scale/Scope**: 小規模（3ファイル変更: Controller 1, Template 1, CSS 1）

## Constitution Check

| 原則 | 評価 | 備考 |
|------|------|------|
| I. Data Integrity First | ✅ 適合 | データ書き込みなし。読み取り専用の表示変更のみ |
| II. Layered Architecture | ✅ 適合 | Symfony 層のみ変更。Python/MySQL スキーマ層は非接触 |
| III. Security & Injection Prevention | ✅ 適合 | Twig の auto-escape を維持。Doctrine QueryBuilder でパラメータバインディング使用 |
| IV. Simplicity & MVP | ✅ 適合 | 新抽象層なし。既存クラス・CSS を最小限修正 |
| V. Observability | N/A | スクレイピング変更なし。表示のみの変更 |

**Gate result**: PASS。Phase 0 研究に進む。

## Project Structure

### Documentation (this feature)

```text
specs/001-details-ux/
├── plan.md              # このファイル
├── research.md          # Phase 0 出力
├── data-model.md        # Phase 1 出力
├── contracts/           # なし（内部 Web ページのため）
└── tasks.md             # Phase 2 出力（/speckit.tasks で生成）
```

### Source Code (repository root)

```text
ship_info/
├── src/
│   └── Controller/
│       └── DetailsController.php        # クエリ修正（日付フィルタ・ソート）
├── templates/
│   └── details/
│       └── index.html.twig              # テンプレート全面リファクタリング
└── public/
    └── css/
        └── styles.css                   # バッジスタイル追加・suspend クラス追加
```

**Structure Decision**: 既存の Symfony 単一プロジェクト構成を踏襲。新規ファイル作成なし。

## Complexity Tracking

Constitution 違反なし。このセクションは空。
