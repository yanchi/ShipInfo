<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260308000001 extends AbstractMigration
{
    public function getDescription(): string
    {
        return 'Change status column from VARCHAR(50) to JSON to support multiple status classes';
    }

    public function up(Schema $schema): void
    {
        // 既存の文字列データを JSON 配列に変換してからカラム型を変更
        $this->addSql("UPDATE operations SET status = JSON_ARRAY(status) WHERE status IS NOT NULL AND JSON_VALID(status) = 0");
        $this->addSql('ALTER TABLE operations CHANGE status status LONGTEXT DEFAULT NULL COMMENT \'(DC2Type:json)\'');
    }

    public function down(Schema $schema): void
    {
        // JSON 配列を単一値（先頭要素）に変換してから VARCHAR(50) へ戻す
        // COALESCE で空配列の場合に既存値を保持。JSON_VALID = 0 の非JSON値はそのまま型変換へ
        $this->addSql("UPDATE operations SET status = COALESCE(JSON_UNQUOTE(JSON_EXTRACT(status, '$[0]')), status) WHERE status IS NOT NULL AND JSON_VALID(status) = 1");
        $this->addSql('ALTER TABLE operations CHANGE status status VARCHAR(50) DEFAULT NULL');
    }
}
