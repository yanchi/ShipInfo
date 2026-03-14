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
        // 先にカラム型を拡張してから JSON 配列化（VARCHAR(50) のまま UPDATE すると文字数増で切り捨てリスクがあるため）
        $this->addSql('ALTER TABLE operations CHANGE status status LONGTEXT DEFAULT NULL COMMENT \'(DC2Type:json)\'');
        $this->addSql("UPDATE operations SET status = JSON_ARRAY(status) WHERE status IS NOT NULL AND JSON_VALID(status) = 0");
    }

    public function down(Schema $schema): void
    {
        // JSON 配列から先頭要素を取り出して単一値に戻してから型変更
        $this->addSql("UPDATE operations SET status = JSON_UNQUOTE(JSON_EXTRACT(status, '$[0]')) WHERE status IS NOT NULL AND JSON_VALID(status) = 1");
        $this->addSql('ALTER TABLE operations CHANGE status status LONGTEXT DEFAULT NULL');
    }
}
